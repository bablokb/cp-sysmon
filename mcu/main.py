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

_serial = None
data_source = getattr(config,"DATA_SOURCE","usb")

def init_serial():
  """ initialize of serial """
  global _serial
  if data_source == 'usb':
    import usb_cdc
    if not usb_cdc.data:
      raise ValueError("need to enable usb_cdc.data in boot.py!")
    else:
      _serial = usb_cdc.data
  else:
    _serial = busio.UART(data_source[1], data_source[0],
                         baudrate=115200)

def get_data():
  """ read data from data-source """

  # read configuration data (lines starting with a #)
  line = '#'
  cfg = ''
  while line[0] == '#':
    line = _serial.readline().decode()
    if line[0] == '#':
      # add configuration line to config (skip comments)
      if line[1:] and line[1:][0] != '#':
        cfg += line[1:]
    else:
      # a real data line, so break
      break

  # process data/configuration
  if cfg:
    # update configuration and ui-objects
    config_ui.parse(cfg)
    config_ui.create_view()
    _serial.write(b"READY\n")
    _serial.flush()
  elif not config_ui.view:
    # received data line without initial ui-configuration, use default
    config_ui.create_view()
    # catch up with the host
    _serial.reset_input_buffer()
    return []

  # parse data
  data = line.strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*len(data), data) for val in pair]

# --- main loop   ------------------------------------------------------------

init_serial()
while True:
  start = time.monotonic()
  values = get_data()
  if values:
    try:
      config_ui.view.set_values(values)
      config.display.refresh()
    except Exception as ex:
      print(f"display update failed with exception: {ex}")
  #print(f"{time.monotonic()-start:0.1f}")  # show framerate
