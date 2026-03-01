###########################################################
# Timing                                                  #
###########################################################

# 100 MHz clock on EMCCLK input
create_clock \
  -period 10.0 \
  -name emcClk \
  [get_ports emcClk]

# EMCCLK is not clock input, so allow it here
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets emcClk_IBUF]

###########################################################
# Pins                                                    #
###########################################################

# EMCCLK
set_property -dict { \
  PACKAGE_PIN AL20 \
  IOSTANDARD LVCMOS18 \
} [get_ports { emcClk }];

# LEDs 0-3
set_property -dict { \
  PACKAGE_PIN BB32 \
  IOSTANDARD LVCMOS12 \
} [get_ports { leds[0] }];
set_property -dict { \
  PACKAGE_PIN BF32 \
  IOSTANDARD LVCMOS12 \
} [get_ports { leds[1] }];
set_property -dict { \
  PACKAGE_PIN AN25 \
  IOSTANDARD LVCMOS12 \
} [get_ports { leds[2] }];
set_property -dict { \
  PACKAGE_PIN AR28 \
  IOSTANDARD LVCMOS12 \
} [get_ports { leds[3] }];

# GPIO2 SMA
#set_property -dict { \
#  PACKAGE_PIN AW22 \
#  IOSTANDARD LVCMOS18 \
#} [get_ports { gpio2 }]; # IO pin
#set_property -dict { \
#  PACKAGE_PIN AW23 \
#  IOSTANDARD LVCMOS18 \
#} [get_ports { gpio2_dir }]; # Dir control (0 = in, 1 = out)

# GPIO3 SMA
#set_property -dict { \
#  PACKAGE_PIN BA21 \
#  IOSTANDARD LVCMOS18 \
#} [get_ports { gpio3 }]; # IO pin
#set_property -dict { \
#  PACKAGE_PIN BC24 \
#  IOSTANDARD LVCMOS18 \
#} [get_ports { gpio3_dir }]; # Dir control (0 = in, 1 = out)
