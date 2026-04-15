source [find interface/ftdi/digilent_jtag_smt2_nc.cfg]
transport select jtag
adapter speed 20000

jtag newtap XCVU13P tap -irlen 24 -expected-id 0x04b51093
init

irscan XCVU13P.tap 0x28A28A
