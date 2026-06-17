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

import busio
import time

# --- hardware and UI configuration   ----------------------------------------

import config
from uiconfig import UIConfig
config_ui = UIConfig()             # single global UI configuration object

# --- helpers for system statistics   ----------------------------------------

_reader = None
data_source = getattr(config,"DATA_SOURCE","usb")

def init_serial():
  """ initialize of serial """
  global _reader
  if data_source == 'usb':
    import usb_cdc
    if not usb_cdc.data:
      raise ValueError("need to enable usb_cdc.data in boot.py!")
    else:
      _reader = usb_cdc.data
  else:
    _reader = busio.UART(data_source[1], data_source[0],
                         baudrate=115200)

def get_data():
  """ read data from data-source """

  # read configuration data (lines starting with a #)
  line = '#'
  cfg = ''
  while line[0] == '#':
    line = _reader.readline().decode()
    if line[0] == '#':
      # add configuration line to config (skip comments)
      if line[1:] and line[1:][0] != '#':
        cfg += line[1:]
    else:
      # a real data line, so break
      break
  if cfg:
    # update configuration and ui-objects
    config_ui.parse(cfg)

  # parse data
  data = line.strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*len(data), data) for val in pair]
  return data

# --- main loop   ------------------------------------------------------------

init_serial()
while True:
  start = time.monotonic()
  values = get_data()
  if not config_ui.view:
    config_ui.create_view()
  config_ui.view.set_values(values)
  config.display.refresh()
  #print(f"{time.monotonic()-start:0.1f}")  # show framerate
