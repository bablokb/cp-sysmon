# ----------------------------------------------------------------------------
# Configuration settings for a ST7789 display with screensize of 320x170:
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import board
from dataviews.Base import Color

# --- basic configuration (optional)   ---------------------------------------

#DEBUG     = False
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
HEIGHT     = 170
ROTATION   =  90
ROW_START  = 0
COL_START  = 35
BRIGHTNESS = 1.0

PIN_SCLK = board.GP10
PIN_MOSI = board.GP11
PIN_CS   = board.GP14
PIN_DC   = board.GP13
PIN_RST  = board.GP12
PIN_BL   = board.GP15

BAUDRATE = 40_000_000

# --- display creation   ------------------------------------------------------

display = None
if display is None:
  import busio
  import fourwire
  import displayio
  from adafruit_st7789 import ST7789

  displayio.release_displays()
  _kwargs = {'rotation': ROTATION,
             'backlight_pin': PIN_BL, 'brightness': BRIGHTNESS,
             'rowstart': ROW_START, 'colstart': COL_START
             }
  _spi    = busio.SPI(clock=PIN_SCLK,MOSI=PIN_MOSI)
  _bus = fourwire.FourWire(_spi,command=PIN_DC,chip_select=PIN_CS,
                           reset=PIN_RST, baudrate=BAUDRATE)
  display = ST7789(_bus, width=WIDTH, height=HEIGHT, **_kwargs)
  display.auto_refresh = False
