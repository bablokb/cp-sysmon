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

DEBUG = False

import busio
import time

# --- hardware and UI configuration   ----------------------------------------

import config
from uiconfig import UIConfig
config_ui = UIConfig()             # single global UI configuration object

# --- print debug message   --------------------------------------------------

def debug(msg):
  """ print debug message """
  if DEBUG:
    print(msg)

# --- initialize serial interface   ------------------------------------------

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
  _serial.reset_input_buffer()
  _serial.write(b"STARTED\n")
  _serial.flush()

# --- read data from serial   -------------------------------------------------

def get_data():
  """ read data from data-source """

  # read configuration data (lines starting with a #)
  line = '#'
  cfg = ''
  while line[0] == '#':
    line = _serial.readline().decode()[:-1]
    debug(f"received: {line}")
    if line and line[0] == '#':
      # add configuration line to config (skip comments)
      if line[1:] and line[1:][0] != '#':
        cfg += line[1:]
    else:
      # a real data line, so break
      break

  # process data/configuration
  if line == "STARTED":
    # cleanup for (re-) start
    debug("STARTED received, cleaning up")
    _serial.reset_input_buffer()
    config_ui.view = None
    _serial.write(b"READY\n")
    _serial.flush()
    return []

  if cfg:
    # update configuration and ui-objects
    debug("updating UI configuration from host")
    config_ui.parse(cfg)
    config_ui.create_view()
    _serial.write(b"READY\n")
    _serial.flush()
    return []
  elif not config_ui.view:
    # configuration not yet available
    return []

  # parse data
  data = line.strip('\n').split(',')
  data = [float(d) for d in data]
  return [val for pair in zip([None]*len(data), data) for val in pair]

# --- main loop   ------------------------------------------------------------

debug("initializing")
init_serial()

debug("waiting for data...")
ts_old = time.monotonic()
while True:
  values, ts = get_data(), time.monotonic()
  if values:
    debug(f"interval: {ts-ts_old:0.1f}")  # show framerate
    ts_old = ts
    try:
      config_ui.view.set_values(values)
      config.display.refresh()
      debug(f"refresh:  {time.monotonic()-ts:0.1f}")
    except Exception as ex:
      debug(f"display update failed with exception: {ex}")
