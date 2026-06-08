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

# --- hardware and UI configuration   ----------------------------------------

import config
from uiconfig import UIConfig
config_ui = UIConfig()             # single global UI configuration object

# --- helpers for system statistics   ----------------------------------------

_usb_serial = None
_uart = None
data_source = getattr(config,"DATA_SOURCE","usb")

def get_data_usb():
  """ read data from USB """
  global _usb_serial
  if not _usb_serial:
    import usb_cdc
    if not usb_cdc.data:
      raise ValueError("need to enable usb_cdc.data in boot.py!")
    else:
      _usb_serial = usb_cdc.data
  return _usb_serial.readline()

def get_data_uart():
  """ read data from UART """
  global _uart
  if not _uart:
    _uart = busio.UART(data_source[1], data_source[0],
                       baudrate=115200)
   return _uart.readline()

def get_data():
  """ read data from data-source """

  # read configuration data (lines starting with a #)
  line = '#'
  cfg = ''
  while line[0] == '#':
    if data_source == 'usb':
      line = get_data_usb()
    else:
      line = get_data_uart()
    if line[0] == '#':
      # add configuration line to config (skip comments)
      if line[1:] and line[1:][0] != '#':
        cfg += line[1:]
    else:
      # a real data line, so break
      break
  if config:
    # update configuration and ui-objects
    config_ui.parse(cfg)

  # parse data
  data = line.decode().strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*4, data) for val in pair]
  return data

# --- main loop   ------------------------------------------------------------

while True:
  values = get_data()
  if not config_ui.view:
    config_ui.create_view()
  config_ui.view.set_values(values)
  config.display.refresh()
