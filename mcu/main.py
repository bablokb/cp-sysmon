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

import config

# --- system statistics configuration   ----------------------------------------

# Note: this is the default configuration. The connected host can override
#       this configuration. See the Readme for details.

CONFIG_UI = {
  'labels':  ["CPU:",     "Mem:",     "Disk:",    "Temp:"],
  'formats': ["{0:.1f}%", "{0:.1f}%", "{0:.1f}%", "{0}°C"],
  'ranges':  [(0,100),    (0,100),    (0,100),    (35,85)],
  'colors':  [
    [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
    [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
    [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
    [(Color.GREEN,65),(Color.YELLOW,80),(Color.RED,None)],
    ],
  }

# TODO: create after reading config from host!
n_bars  = len(CONFIG_UI['labels'])
formats = zip(CONFIG_UI['labels'], CONFIG_UI['formats'])
ranges  = CONFIG_UI['ranges']
colors  = CONFIG_UI['colors']

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
    _uart = busio.UART(config.DATA_SOURCE[1], config.DATA_SOURCE[0],
                       baudrate=115200)
  data = _uart.readline().decode().strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*4, data) for val in pair]

def get_data():
  """ read data from data-source """
  if config.DATA_SOURCE == 'usb':
    data = get_data_usb()
  else:
    data = get_data_uart()
  #print(f"{data=}")
  return data

# --- create display and UI objects   -----------------------------------------

config.display.auto_refresh=False

bars = [None]*n_bars
for i in range(n_bars):
  bars[i] = (0,2*i+1,DataBar(size=(config.BAR_WIDTH,
                                   config.BAR_HEIGHT),range=ranges[i],
                             format=formats[2*i+1],
                             color=colors[i],
                             text_color=Color.AQUA,
                             text_justify=Justify.RIGHT,
                             font=config.FONT,
                             bg_color=Color.BLACK))

# create view with n_bars rows (right align labels)
view = DataView(
  dim=(n_bars,2),
  width=config.display.width,height=config.display.height,
  justify=Justify.RIGHT,
  fontname=config.FONT,
  formats=formats,
  border=1,
  divider=1,
  padding=3,
  bg_color=Color.BLACK,
  col_width=[0,1],
  objects = bars
)

# left align hbars
for index in range(1,2*n_bars,2):
  view.justify(Justify.LEFT,index=index)

config.display.root_group = view

# --- main loop   ------------------------------------------------------------

while True:
  view.set_values(get_data())
  config.display.refresh()
