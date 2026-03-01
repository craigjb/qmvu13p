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
set_property -dict { \
  PACKAGE_PIN AL20 \
  IOSTANDARD LVCMOS18 \
} [get_ports { emcClk }];

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
