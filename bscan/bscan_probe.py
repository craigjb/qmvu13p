import sys
import time
import socket
import re
import subprocess
import argparse

# Configuration
OPENOCD_HOST = "127.0.0.1"
OPENOCD_PORT = 4444
TAP_NAME = "XCVU13P.tap"
BSCAN_SAMPLE = "0x41041"
BSCAN_LEN = 3716

DEBOUNCE_THRESHOLD = 3


def parse_ignore_list(filepath):
    ignore_set = set()
    if not filepath:
        return ignore_set
    try:
        with open(filepath, "r") as f:
            for line in f:
                name = line.strip()
                if name and not name.startswith("#"):
                    ignore_set.add(name)
        print(f"[*] Parsed Ignore List: Ignoring {len(ignore_set)} explicit pins.")
        return ignore_set
    except FileNotFoundError:
        print(f"[!] Warning: Ignore file '{filepath}' not found.")
        return set()


def parse_bsdl_mapping(filepath, ignore_set):
    mapping = {}
    pattern = re.compile(r"(\d+)\s*\([^,]+,\s*(IO_[a-zA-Z0-9_]+),\s*([^,]+)")
    try:
        with open(filepath, "r") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    cell_idx = int(match.group(1))
                    io_name = match.group(2).strip()
                    func = match.group(3).strip()
                    if io_name not in ignore_set:
                        mapping[cell_idx] = f"{io_name} ({func})"
        print(f"[*] Parsed BSDL: Monitoring {len(mapping)} physical IO cells.")
        return mapping
    except FileNotFoundError:
        print(f"[!] Error: Could not find BSDL file '{filepath}'.")
        sys.exit(1)


def send_openocd_cmd(sock, cmd):
    sock.sendall((cmd + "\n").encode("utf-8"))
    response = ""
    while True:
        chunk = sock.recv(4096).decode("utf-8", errors="ignore")
        response += chunk
        if "> " in response:
            break
    return response


def start_openocd(cfg_file):
    """Launches OpenOCD as a background process."""
    print(f"[*] Launching OpenOCD with config: {cfg_file}")
    try:
        # Route stdout/stderr to DEVNULL to keep our terminal clean for pin probing
        proc = subprocess.Popen(
            ["openocd", "-f", cfg_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Give OpenOCD a second to initialize the JTAG chain and open the telnet port
        time.sleep(1.5)

        if proc.poll() is not None:
            print(
                "[!] Error: OpenOCD process died immediately. Check your config file and hardware connection."
            )
            sys.exit(1)

        return proc
    except FileNotFoundError:
        print(
            "[!] Error: 'openocd' command not found. Is it installed and in your system PATH?"
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="JTAG Boundary Scan Pin Prober")
    parser.add_argument(
        "-b", "--bsdl", required=True, help="Path to the BSDL cell definition file"
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Path to the OpenOCD configuration file"
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="Optional path to a text file with pins to ignore",
        default=None,
    )

    args = parser.parse_args()

    ignore_set = parse_ignore_list(args.ignore)
    cell_map = parse_bsdl_mapping(args.bsdl, ignore_set)
    hex_pattern = re.compile(r"\b[0-9a-fA-F]{100,}\b")

    # Launch the OpenOCD Subprocess
    ocd_proc = start_openocd(args.config)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((OPENOCD_HOST, OPENOCD_PORT))
        while True:
            if "> " in s.recv(4096).decode("utf-8", errors="ignore"):
                break

        print(f"[*] Loading SAMPLE instruction ({BSCAN_SAMPLE})...")
        send_openocd_cmd(s, f"irscan {TAP_NAME} {BSCAN_SAMPLE}")

        resp = send_openocd_cmd(s, f"drscan {TAP_NAME} {BSCAN_LEN} 0")
        initial_hex = hex_pattern.search(resp).group(0)
        initial_state = bin(int(initial_hex, 16))[2:].zfill(BSCAN_LEN)[::-1]

        stable_states = {i: initial_state[i] for i in range(BSCAN_LEN)}
        last_raw_reads = {i: initial_state[i] for i in range(BSCAN_LEN)}
        consecutive_counts = {i: 1 for i in range(BSCAN_LEN)}
        toggle_tracker = {i: 0 for i in range(BSCAN_LEN)}

        print(
            f"[*] Software Debounce active (requires {DEBOUNCE_THRESHOLD} consecutive stable reads)."
        )
        print("[*] Probe ready! Touch a pin with your pull-up to see it lock on.")
        print("-" * 70)

        while True:
            resp = send_openocd_cmd(s, f"drscan {TAP_NAME} {BSCAN_LEN} 0")
            match = hex_pattern.search(resp)
            if not match:
                continue

            hex_dump = match.group(0)
            current_state = bin(int(hex_dump, 16))[2:].zfill(BSCAN_LEN)[::-1]

            for i in range(BSCAN_LEN):
                if i not in cell_map:
                    continue

                raw_val = current_state[i]

                if raw_val == last_raw_reads[i]:
                    consecutive_counts[i] += 1
                else:
                    consecutive_counts[i] = 1
                    last_raw_reads[i] = raw_val

                if consecutive_counts[i] >= DEBOUNCE_THRESHOLD:
                    if raw_val != stable_states[i]:
                        stable_states[i] = raw_val
                        toggle_tracker[i] += 1

                        arrow = "🟩 UP  " if raw_val == "1" else "🟥 DOWN"
                        print(
                            f"{arrow} | {cell_map[i]:<25} | Cell: {i:<4} | Total Taps: {toggle_tracker[i]}"
                        )

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[*] Stopping scan. Happy reverse engineering!")
    except ConnectionRefusedError:
        print(
            f"\n[!] Connection refused. OpenOCD might have failed to bind to port {OPENOCD_PORT}."
        )
    except Exception as e:
        print(f"\n[!] Error: {e}")
    finally:
        # Clean up the connection and kill the OpenOCD background process
        s.close()
        print("[*] Terminating OpenOCD subprocess...")
        ocd_proc.terminate()
        ocd_proc.wait()


if __name__ == "__main__":
    main()
