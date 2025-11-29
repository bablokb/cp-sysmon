# ----------------------------------------------------------------------------
# Show system statistics using DataBars.
#
# This program displays system statistics on a small display. The data
# is read from a serial, either usb or uart.
#
# This is the partner program for the program cp_sysmon.py that is expected
# to run on the PC and collect and send data.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import board
import busio
import time

try:
  import psutil
except:
  pass

from dataviews.Base import Color, Justify
from dataviews.DisplayFactory import DisplayFactory
from dataviews.DataView  import DataView
from dataviews.DataPanel import DataPanel, PanelText
from dataviews.DataBar import DataBar

# --- core configuration   ---------------------------------------------------

DATA_SOURCE = 'usb'  # 'usb' or (rx-pin,tx-pin)

# --- display configuration   ------------------------------------------------

# values optimized for 240x135 displays, e.g. Adafruit Mini-Pi-TFT
# or the display integrated into the Waveshare RP2040-Geek.
# Other displays need other values, especially if you add more statistics
WIDTH      = 240
HEIGHT     = 135
BAR_WIDTH  = 180
BAR_HEIGHT =  30
FONT       = 'fonts/DejaVuSans-16-subset.bdf'

# Waveshare RP2040-Geek: use board.DISPLAY

# Adafruit Mini-Pi-TFT, using Pico-to-Pi adapter
#spi = busio.SPI(clock=board.SCLK,MOSI=board.MOSI)
#PIN_CS   = board.CE0
#PIN_DC   = board.GPIO25
#PIN_RST  = None
#driver   = 'st7789'
#args     = [PIN_DC, PIN_CS]
#kwargs   = {'pin_rst': PIN_RST, 'spi': spi,
#            'rotation': 90, 'rowstart': 40, 'colstart': 53}

# Waveshare Pico-Res-Touch-LCD 2.8
WIDTH      = 320
HEIGHT     = 240
BAR_WIDTH  = 240
BAR_HEIGHT =  50
FONT       = 'fonts/DejaVuSans-16-subset.bdf'

spi = busio.SPI(clock=board.GP10,MOSI=board.GP11)
PIN_CS   = board.GP9
PIN_DC   = board.GP8
PIN_RST  = board.GP15
PIN_BL   = board.GP13
driver   = 'st7789'
args     = [PIN_DC, PIN_CS]
kwargs   = {'pin_rst': PIN_RST, 'spi': spi,
            'rotation': 90, 'rowstart': 0, 'colstart': 0,
            'backlight_pin': PIN_BL, 'backlight_pwm_frequency': 100}

# --- system statistics configuration   ----------------------------------------

BAR_N      =   4  # cpu, memory, disk, temperature

formats = ["CPU:", "{0:.1f}%",
           "Mem:", "{0:.1f}%",
           "Disk:","{0:.1f}%",
           "Temp:","{0}°C",]
ranges = [
  (0,100),
  (0,100),
  (0,100),
  (35,85),
  ]
colors = [
  [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
  [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
  [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
  [(Color.GREEN,65),(Color.YELLOW,80),(Color.RED,None)],
  ]

# --- helpers for system statistics   ----------------------------------------

_usb_serial = None
def get_data_usb():
  """ read data from USB """
  global _usb_serial
  if not _usb_serial:
    import usb_cdc
    if not usb_cdc.data:
      raise ValueError("need to enable usb_cdc.data in boot.py!")
    else:
      _usb_serial = usb_cdc.data
  data = _usb_serial.readline().decode().strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*4, data) for val in pair]

_uart = None
def get_data_uart():
  """ read data from UART """
  global _uart
  if not _uart:
    _uart = busio.UART(DATA_SOURCE[1], DATA_SOURCE[0], baudrate=115200)
  data = _uart.readline().decode().strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*4, data) for val in pair]

def get_data():
  """ read data from data-source """
  if DATA_SOURCE == 'usb':
    data = get_data_usb()
  else:
    data = get_data_uart()
  #print(f"{data=}")
  return data

# --- create display and UI objects   -----------------------------------------

if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  display = getattr(DisplayFactory,driver)(*args,width=WIDTH,height=HEIGHT,
                                           **kwargs)
display.auto_refresh=False

bars = [None]*BAR_N
for i in range(BAR_N):
  bars[i] = (0,2*i+1,DataBar(size=(BAR_WIDTH,BAR_HEIGHT),range=(0,100),
                             format=formats[2*i+1],
                             color=colors[i],
                             text_color=Color.AQUA,
                             text_justify=Justify.RIGHT,
                             font=FONT,
                             bg_color=Color.BLACK))

# create view with BAR_N rows (right align labels)
view = DataView(
  dim=(BAR_N,2),
  width=display.width,height=display.height,
  justify=Justify.RIGHT,
  fontname=FONT,
  formats=formats,
  border=1,
  divider=1,
  padding=3,
  bg_color=Color.BLACK,
  col_width=[0,1],
  objects = bars
)

# left align hbars
for index in range(1,2*BAR_N,2):
  view.justify(Justify.LEFT,index=index)

display.root_group = view

# --- main loop   ------------------------------------------------------------

while True:
  view.set_values(get_data())
  display.refresh()
