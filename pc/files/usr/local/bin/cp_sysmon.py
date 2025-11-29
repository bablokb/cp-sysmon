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

import serial
import psutil
import time
import os
import sys

BAUD = 115200          # communication speed on serial
CPU_TEMP_LABEL = 'CPU' # depends on the system
DISK_MOUNT = '/'       # depends on preferences
INTERVAL = 1           # depends on update speed of display partner program

def get_temp():
  """ return CPU-temperature """
  temps = psutil.sensors_temperatures()
  for hw in temps.values():
    for value in hw:
      if value.label == CPU_TEMP_LABEL:
        return int(round(value.current,0))
  return 0

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
    time.sleep(INTERVAL)
  # create serial
  if ser is None:
    time.sleep(0.25)                # give udev time to set permissions
    ser = serial.Serial(port,BAUD)
    print(f"serial device created")
  data = [f"{psutil.cpu_percent()}",
          f"{psutil.virtual_memory().percent}",
          f"{psutil.disk_usage(DISK_MOUNT).percent}",
          f"{get_temp()}"]
  #print(f"{data=}")
  try:
    ser.write(bytes(f"{','.join(data)}\n",'UTF-8'))
  except:
    ser.close()
    ser = None
  time.sleep(INTERVAL)
