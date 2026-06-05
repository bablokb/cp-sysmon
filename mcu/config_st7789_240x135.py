# ----------------------------------------------------------------------------
# Configuration settings for a ST7789 display with screensize of 240x135:
#   - Adafruit Mini-Pi-TFT
#   - the display integrated into the Waveshare RP2040-Geek
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import board

# --- core configuration   ---------------------------------------------------

DATA_SOURCE = 'usb'  # 'usb' or (rx-pin,tx-pin)
BAR_WIDTH   = 180
BAR_HEIGHT  =  30
FONT        = 'fonts/DejaVuSans-16-subset.bdf'

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

if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  import busio
  import fourwire
  from adafruit_st7789 import ST7789

  _kwargs = {'rotation': ROTATION, 'rowstart': ROW_START, 'colstart': COL_START}
  _spi    = busio.SPI(clock=PIN_SCLK,MOSI=PIN_MOSI)
  _bus = fourwire.FourWire(_spi,command=PIN_DC,chip_select=PIN_CS,
                           reset=PIN_RST)
  display = ST7789(_bus,**_kwargs)
