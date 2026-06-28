# ----------------------------------------------------------------------------
# Configuration settings for a ST7789 display with screensize of 240x135:
#   - Adafruit Mini-Pi-TFT
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

WIDTH      = 240
HEIGHT     = 135
ROTATION   = 90
ROW_START  = 40
COL_START  = 53

PIN_SCLK = board.SCLK
PIN_MOSI = board.MOSI
PIN_CS   = board.CE0
PIN_DC   = board.GPIO25
PIN_RST  = None

# --- display creation   ------------------------------------------------------

display = None
if display is None:
  import busio
  import fourwire
  import displayio
  from adafruit_st7789 import ST7789

  displayio.release_displays()
  _kwargs = {'rotation': ROTATION, 'rowstart': ROW_START, 'colstart': COL_START}
  _spi    = busio.SPI(clock=PIN_SCLK,MOSI=PIN_MOSI)
  _bus = fourwire.FourWire(_spi,command=PIN_DC,chip_select=PIN_CS,
                           reset=PIN_RST)
  display = ST7789(_bus, width=WIDTH, height=HEIGHT, **_kwargs)
  display.auto_refresh = False
