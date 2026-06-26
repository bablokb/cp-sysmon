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

import sensors

# --- read configuration from /etc/cp_sysmon.json   -------------------------

try:
  f = open("/etc/cp_sysmon.json")
  cfg = json.load(f)
  f.close()
except:
  cfg = {
    'BAUD': 115200,                             # communication speed on serial
    'INTERVAL': 1.5,                            # depends on speed of MCU
    'SENSORS': ["cpu", "temp", "mem", "disks"], # sensor to use
    'TEMP': ('thinkpad', 'CPU'),                # depends on the system
    'DISK_MOUNTS': ['/'],                       # depends on preferences
    'UI_CONFIG':  {                             # UI configuration
      "labels" : ["CPU:",     "Temp:", "Mem:",     "Disk:"],
      "formats": ["{0:.1f}%", "{0}°C", "{0:.1f}%", "{0:.1f}%"],
      "ranges" : [[0,100],    [35,85], [0,100],    [0,100]],
      "colors" : [
        [["0x008000",70],["0xFFFF00",85],["0xFF0000",None]],
        [["0x008000",65],["0xFFFF00",80],["0xFF0000",None]],
        [["0x008000",70],["0xFFFF00",85],["0xFF0000",None]],
        [["0x008000",70],["0xFFFF00",85],["0xFF0000",None]]
        ]
      }
    }

# --- wait for MCU   ---------------------------------------------------------

def wait_for_mcu(ser):
  """ wait until MCU signal ready """
  print("waiting for MCU...")
  start = time.monotonic()
  while True:
    resp = ser.readline().decode('utf-8')[:-1]
    print(f"{resp=}")
    if resp in ["READY", "STARTED"]:
      print(f"MCU {resp} after {time.monotonic()-start:0.1f}s")
      return

# --- send configuration   ---------------------------------------------------

def send_configuration(ser):
  """ send configuration to MCU """

  try:
    print("sending ui-configuration to MCU...")
    ser.write(bytes(f"#{json.dumps(cfg['UI_CONFIG'])}\n\n","UTF-8"))
    wait_for_mcu(ser)
  except Exception as ex:
    print(f"failed to write UI_CONFIG: {ex}")

# --- main   -----------------------------------------------------------------

#print(f"ui_config: {cfg['UI_CONFIG']}")
if len(sys.argv) < 2:
  port = "/dev/ttyACM1"
else:
  port = sys.argv[1]
  if not port.startswith('/dev'):
    port = f"/dev/{port}"
print(f"using port {port}")
ser = None

sensors = sensors.Sensors(cfg)
while True:
  start = time.monotonic()
  # wait for serial device
  while ser is None and not os.path.exists(port):
    print(f"waiting for {port}") 
    time.sleep(cfg["INTERVAL"])

  # create serial
  if ser is None:
    time.sleep(0.25)                # give udev time to set permissions
    ser = serial.Serial(port,cfg["BAUD"], timeout=1)
    print(f"serial device created")
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
      print(f"OSerror {osex} for serial (MCU removed?).")
      try:
        ser.close()
      except:
        pass
      finally:
        ser = None
        continue

  # query and send data
  data = []
  for name in cfg["SENSORS"]:
    data.extend([f"{value}" for value in sensors.get_data(name)])

  print(f"{data=}")
  try:
    ser.write(bytes(f"{','.join(data)}\n",'UTF-8'))
  except OSError as osex:
    print(f"OSerror {osex} for serial (MCU removed?).")
    try:
      ser.close()
    except:
      pass
    finally:
      ser = None
      continue
  except Exception as ex:
    print(f"sending data failed with {ex} for: {data=}")
  time.sleep(max(0,
                 cfg["INTERVAL"]-(time.monotonic()-start)
                 )
             )
