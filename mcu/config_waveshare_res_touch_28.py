# ----------------------------------------------------------------------------
# Configuration settings for the Waveshare Res Touch LCD 2.8.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import board

# --- core configuration   ---------------------------------------------------

DATA_SOURCE = 'usb'  # 'usb' or (rx-pin,tx-pin)
BAR_WIDTH   = 240
BAR_HEIGHT  =  50
FONT        = 'fonts/DejaVuSans-16-subset.bdf'

# --- display configuration   ------------------------------------------------

WIDTH      = 320
HEIGHT     = 240
ROTATION   = 90
ROW_START  = 0
COL_START  = 0

PIN_SCLK = board.SCLK
PIN_MOSI = board.MOSI
PIN_CS   = board.GP9
PIN_DC   = board.GP8
PIN_RST  = board.GP15
PIN_BL   = board.GP13

# --- display creation   ------------------------------------------------------

if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  import busio
  import fourwire
  from adafruit_st7789 import ST7789

  _kwargs = {'rotation': ROTATION, 'rowstart': ROW_START, 'colstart': COL_START,
             'backlight_pin': PIN_BL, 'backlight_pwm_frequency': 100}

  _spi    = busio.SPI(clock=PIN_SCLK,MOSI=PIN_MOSI)
  _bus = fourwire.FourWire(_spi,command=PIN_DC,chip_select=PIN_CS,
                           reset=PIN_RST)
  display = ST7789(_bus,**_kwargs)
