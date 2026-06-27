#!/usr/bin/python3
# ----------------------------------------------------------------------------
# cp_sysmon.py
#
# Write system statistics to a serial.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ---------------------------------------------------------------------------

import json
import os
import psutil
import serial
import sys
import time

from sysmon_sensors import Sensors

# --- read configuration from /etc/cp_sysmon.json   -------------------------

# fill defaults
cfg = {
  'DEBUG': False,                             # output debug messages
  'BAUD': 115200,                             # communication speed on serial
  'INTERVAL': 1.5,                            # depends on speed of MCU
  'SENSORS': ["cpu", "temp", "mem", "disks"], # sensor to use
  'TEMP': ('thinkpad', 'CPU'),                # depends on the system
  'DISK_MOUNTS': ['/'],                       # depends on preferences
  }

try:
  f = open("/etc/cp_sysmon.json")
  cfg_new = json.load(f)
  f.close()
  cfg.update(cfg_new)  # update cfg dict
except:
  pass

sensors = Sensors(cfg)
sensors.update_ui_config()

# --- print debug message   --------------------------------------------------

def debug(msg):
  """ print debug message """
  if cfg['DEBUG']:
    print(msg)

# --- wait for MCU   ---------------------------------------------------------

def wait_for_mcu(ser):
  """ wait until MCU signal ready """
  debug("waiting for MCU...")
  start = time.monotonic()
  while True:
    resp = ser.readline().decode('utf-8')[:-1]
    debug(f"{resp=}")
    if resp in ["READY", "STARTED"]:
      debug(f"MCU {resp} after {time.monotonic()-start:0.1f}s")
      return

# --- send configuration   ---------------------------------------------------

def send_configuration(ser):
  """ send configuration to MCU """

  try:
    debug("sending ui-configuration to MCU...")
    ser.write(bytes(f"#{json.dumps(cfg['UI_CONFIG'])}\n\n","UTF-8"))
    wait_for_mcu(ser)
  except Exception as ex:
    debug(f"failed to write UI_CONFIG: {ex}")

# --- main   -----------------------------------------------------------------

debug(f"ui_config: {cfg['UI_CONFIG']}")
if len(sys.argv) < 2:
  port = "/dev/ttyACM1"
else:
  port = sys.argv[1]
  if not port.startswith('/dev'):
    port = f"/dev/{port}"
debug(f"using port {port}")
ser = None

while True:
  start = time.monotonic()
  # wait for serial device
  while ser is None and not os.path.exists(port):
    debug(f"waiting for {port}")
    time.sleep(cfg["INTERVAL"])

  # create serial
  if ser is None:
    time.sleep(0.25)                # give udev time to set permissions
    try:
      ser = serial.Serial(port,cfg["BAUD"], timeout=1)
    except Exception as ex:
      debug("could not open serial port. Exception: {ex}")
      continue
    debug(f"serial device created")
    ser.write(bytes("STARTED\n","UTF-8"))
    wait_for_mcu(ser)
    send_configuration(ser)
  else:
    try:
      if ser.in_waiting:
        resp = ser.readline().decode('utf-8')[:-1]
        if resp == "STARTED":
          send_configuration(ser)
    except OSError as osex:
      debug(f"OSerror {osex} for serial (MCU removed?).")
      try:
        ser.close()
      except:
        pass
      finally:
        ser = None
        continue

  # query and send data
  data = sensors.get_data()
  debug(f"{data=}")
  try:
    ser.write(bytes(f"{','.join(data)}\n",'UTF-8'))
  except OSError as osex:
    debug(f"OSerror {osex} for serial (MCU removed?).")
    try:
      ser.close()
    except:
      pass
    finally:
      ser = None
      continue
  except Exception as ex:
    debug(f"sending data failed with {ex} for: {data=}")
  time.sleep(max(0,
                 cfg["INTERVAL"]-(time.monotonic()-start)
                 )
             )
