# ----------------------------------------------------------------------------
# Configuration settings for the Waveshare Res Touch LCD 2.8.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import board
from dataviews.Base import Color

# --- basic configuration (optional)   ---------------------------------------

#FONT      = "fonts/DejaVuSans-16-subset.bdf"
#BG_COLOR  = Color.BLACK
#TXT_COLOR = Color.AQUA
#BORDER    = 1
#PADDING   = 3
#DIVIDER   = 1
#BAR_WIDTH   = 3/4 of display width
#BAR_HEIGHT  = display height divided by n_stats minus border/divider/padding

#DATA_SOURCE = 'usb'  # 'usb' or tuple (rx-pin,tx-pin)

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

display = None
if display is None:
  import busio
  import fourwire
  import displayio
  from adafruit_st7789 import ST7789

  displayio.release_displays()
  _kwargs = {'rotation': ROTATION, 'rowstart': ROW_START, 'colstart': COL_START,
             'backlight_pin': PIN_BL, 'backlight_pwm_frequency': 100}

  _spi    = busio.SPI(clock=PIN_SCLK,MOSI=PIN_MOSI)
  _bus = fourwire.FourWire(_spi,command=PIN_DC,chip_select=PIN_CS,
                           reset=PIN_RST)
  display = ST7789(_bus, width=WIDTH, height=HEIGHT, **_kwargs)
  display.auto_refresh = False
