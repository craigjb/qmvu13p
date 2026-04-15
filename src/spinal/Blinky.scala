package qmvu13p.blinky

import spinal.core._
import spinal.lib._
import spinal.lib.blackbox.xilinx.s7._

case class Blinky() extends Component {
  val io = new Bundle {
    val emcClk = in Bool()
    val leds = out Bits(4 bits)
    val ddr_pins = in Bits(152 bits)
    val io_pins = in Bits(675 bits)
  }
  noIoPrefix()

  val sysClkDomain = ClockDomain(
    clock = BUFG.on(io.emcClk),
    config = ClockDomainConfig(
      resetKind = BOOT
    ),
    frequency = FixedFrequency(100 MHz)
  )

  sysClkDomain on {
    val blinker = RegInit(B"01")
    val timer = Timeout(1 Hz)
    when(timer) {
      blinker := blinker.rotateLeft(1)
      timer.clear()
    }

    io.leds(1 downto 0) := blinker
  }

  io.leds(3) := io.ddr_pins.orR
  io.leds(2) := io.io_pins.orR
}

object TopLevelVerilog extends App {
  SpinalConfig(targetDirectory = "target/spinal")
    .generateVerilog(Blinky())
}
