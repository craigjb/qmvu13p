import asyncio

# In the 'control-gpio' script environment, Glasgow automatically 
# provides the 'gpio_iface' object to interact with the pins.
# Index 0 refers to the first pin you pass in the --pins argument.

print("[*] Configuring pin as output...")
await gpio_iface.output(0, True)

print("[*] Starting 1Hz beacon. Probe away! (Press Ctrl+C to stop)")

try:
    while True:
        await gpio_iface.set(0, True)
        await asyncio.sleep(0.5)
        
        await gpio_iface.set(0, False)
        await asyncio.sleep(0.5)

except KeyboardInterrupt:
    # Safely release the pin back to a high-impedance state when you quit
    print("\n[*] Stopping beacon. Setting pin to High-Z.")
    await gpio_iface.input(0)
