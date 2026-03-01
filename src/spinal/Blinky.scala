package qmvu13p.blinky

import spinal.core._
import spinal.lib._
import spinal.lib.blackbox.xilinx.s7._

case class Blinky() extends Component {
  val io = new Bundle {
    val emcClk = in Bool()
    val leds = out Bits(4 bits)
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
    val blinker = RegInit(B"0001")
    val timer = Timeout(1 Hz)
    when(timer) {
      blinker := blinker.rotateLeft(1)
      timer.clear()
    }

    io.leds := blinker
  }
}

object TopLevelVerilog extends App {
  SpinalConfig(targetDirectory = "target/spinal")
    .generateVerilog(Blinky())
}
