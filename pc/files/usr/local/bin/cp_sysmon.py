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

# --- read configuration from /etc/cp_sysmon.json   -------------------------

try:
  f = open("/etc/cp_sysmon.json")
  cfg = json.load(f)
  f.close()
except:
  cfg = {
    'BAUD': 115200,                          # communication speed on serial
    'TEMP': ('thinkpad', 'CPU'),             # depends on the system
    'DISK_MOUNTS': ['/'],                    # depends on preferences
    'INTERVAL': 1.5,                         # depends on speed of MCU
    'UI_CONFIG': ''                          # UI configuration
    }

def get_temp():
  """ return CPU-temperature """
  try:
    name, label = cfg["TEMP"]
    component = psutil.sensors_temperatures()[name]
    for value in component:
      if value.label == label:
        return int(round(value.current,0))
    return 0
  except:
    return 0

#print(f"ui_config: {cfg['UI_CONFIG']}")
if len(sys.argv) < 2:
  port = "/dev/ttyACM1"
else:
  port = sys.argv[1]
  if not port.startswith('/dev'):
    port = f"/dev/{port}"

print(f"using port {port}")
ser = None
while True:
  # wait for serial device
  while ser is None and not os.path.exists(port):
    print(f"waiting for {port}") 
    time.sleep(cfg["INTERVAL"])

  # create serial
  if ser is None:
    time.sleep(0.25)                # give udev time to set permissions
    ser = serial.Serial(port,cfg["BAUD"])
    print(f"serial device created")

    # send UI configuration
    if cfg["UI_CONFIG"]:
      try:
        ser.write(bytes(f"#{json.dumps(cfg['UI_CONFIG'])}\n","UTF-8"))
      except Exception as ex:
        print(f"failed to write UI_CONFIG: {ex}")

  # query and send data
  data = [f"{psutil.cpu_percent()}",
          f"{get_temp()}",
          f"{psutil.virtual_memory().percent}"]
  for mnt in cfg["DISK_MOUNTS"]:
    data.append(f"{psutil.disk_usage(mnt).percent}")
  #print(f"{data=}")
  try:
    ser.write(bytes(f"{','.join(data)}\n",'UTF-8'))
  except:
    ser.close()
    ser = None
  time.sleep(cfg["INTERVAL"])
