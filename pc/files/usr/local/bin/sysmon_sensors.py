# ----------------------------------------------------------------------------
# sysmon_sensors.py: collection of data-sampling wrappers.
#
# Each wrapper will create a list of values, even if the list is only a
# single item.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ---------------------------------------------------------------------------

import psutil

class Sensors:
  """ data-sampling wrappers """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config
    for sensor in config["SENSORS"]:
      if not hasattr(self,f"_{sensor}"):
        raise ValueError(f"error: sensor {sensor} is not implemented!")

  # --- multiplexer   --------------------------------------------------------

  def get_data(self):
    """ return data for the configured sensors """
    data = []
    for sensor in self._config["SENSORS"]:
      data.extend([f"{value}" for value in getattr(self,f"_{sensor}")()])
    return data

  # --- update UI configuration   --------------------------------------------

  def update_ui_config(self):
    """ update/create config['UI_CONFIG'] """

    cfg = self._config     # as a shortcut

    labels  = []
    formats = []
    ranges  = []
    colors  = []
    for sensor in cfg['SENSORS']:
      ui_cfg = getattr(self,f"_{sensor}")(ui_config=True)
      labels.append(ui_cfg["label"])
      formats.append(ui_cfg["format"])
      ranges.append(ui_cfg["range"])
      colors.append(ui_cfg["colors"])

    # override with sensor-specific values from global config-file
    for index, sensor in enumerate(cfg['SENSORS']):
      cfg_sensor = cfg.get(sensor)
      if not cfg_sensor:
        continue
      for attr in ['labels', 'formats', 'ranges', 'colors']:
        value = cfg_sensor.get(attr)
        if not value:
          continue
        if isinstance(value,list):
          # json does not suppor tuples, so convert lists
          value = tuple(value)
        locals()[attr][index] = value

    # flatten lists and combine them to MCU-compatible format
    labels  = self._flatten(labels)
    formats = self._flatten(formats)
    ranges  = self._flatten(ranges)
    colors  = self._flatten(colors)
    if "UI_CONFIG" not in cfg:
      cfg["UI_CONFIG"] = {}
    if not "labels" in cfg["UI_CONFIG"]:
      cfg["UI_CONFIG"]["labels"]  = labels
    if not "formats" in cfg["UI_CONFIG"]:
      cfg["UI_CONFIG"]["formats"] = formats
    if not "ranges" in cfg["UI_CONFIG"]:
      cfg["UI_CONFIG"]["ranges"]  = ranges
    if not "colors" in cfg["UI_CONFIG"]:
      cfg["UI_CONFIG"]["colors"]  = colors

  # --- helper: flatten list with elements/sublists   ------------------------

  def _flatten(self, inlist):
    """ flatten list with elements/sublists """
    outlist = []
    for list_or_elem in inlist:
      if isinstance(list_or_elem,(list,tuple)):
        for elem in list_or_elem:
          outlist.append(elem)
      else:
        outlist.append(list_or_elem)
    return outlist

  # --- return cpu percent   -------------------------------------------------

  def _cpu(self, ui_config=False):
    """ return CPU """
    if ui_config:
      return {"label": "CPU:",
              "format": "{0:.1f}%",
              "range": [(0,100)],
              "colors": [(("0x008000",70),("0xFFFF00",85),("0xFF0000",None),)]
              }
    else:
      return [psutil.cpu_percent()]

  # --- return detailed cpu usage   ------------------------------------------

  def _cpu_detail(self, ui_config=False):
    """ return CPU-details for info in
    [user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice]
    """
    if ui_config:
      return {"label": ["CPU:"],
              "format": ["{0:.1f}%"],
              "range": [[0,100]],
              "colors": [[("0x008000",70),("0xFFFF00",85),("0xFF0000",None)]]
              }
    else:
      cpu_time_percent = psutil.cpu_times_percent()
      return [getattr(cpu_time_percent,info,0)
              for info in self._config["CPU_DETAILS"]]

  # --- return cpu frequency   -----------------------------------------------

  def _freq(self, ui_config=False):
    """ return CPU frequency """
    if ui_config:
      cpu_freq = psutil.cpu_freq()
      green = int(cpu_freq.min + 0.5*(cpu_freq.max-cpu_freq.min))  # at 50% of range
      orange = int(cpu_freq.min + 0.8*(cpu_freq.max-cpu_freq.min)) # at 80% of range
      return {"label": "Freq:",
              "format": "{0:4.0f}",
              "range": [(cpu_freq.min,cpu_freq.max)],
              "colors": [
                (("0x008000",green),("0xFFFF00",orange),("0xFF0000",None),)]
              }
    else:
      return [int(psutil.cpu_freq().current)]

  # --- return cpu load   ----------------------------------------------------

  def _load(self, ui_config=False):
    """ return CPU load """
    if ui_config:
      return {"label": ["Load:"],
              "format": ["{0:.1f}"],
              "range": [(0,100)],
              "colors": [(("0x008000",70),("0xFFFF00",85),("0xFF0000",None),)]
              }
    else:
      return [load for load in psutil.getloadavg()]

  # --- return system temperature   ------------------------------------------

  def _temp(self, ui_config=False):
    """ return system temperature """
    if ui_config:
      return {"label": ["Temp:"],
              "format": ["{0}°C"],
              "range": [(35,85)],
              "colors": [(("0x008000",65),("0xFFFF00",80),("0xFF0000",None),)]
              }
    else:
      try:
        name = self._config["temp"]["name"]
        label = self._config["temp"]["label"]
        component = psutil.sensors_temperatures()[name]
        for value in component:
          if value.label == label:
            return [int(round(value.current,0))]
        return [0]
      except:
        return [0]

  # --- return memory usage   ------------------------------------------------

  def _mem(self, ui_config=False):
    """ return memory usage """
    if ui_config:
      return {"label": ["Mem:"],
              "format": ["{0:.1f}%"],
              "range": [(0,100)],
              "colors": [(("0x008000",70),("0xFFFF00",85),("0xFF0000",None),)]
              }
    else:
      return [psutil.virtual_memory().percent]

  # --- return used disk-space   ---------------------------------------------

  def _disks(self, ui_config=False):
    """ return used disk-space """
    if ui_config:
      if "disks" not in self._config:
        self._config["disks"] = {}
      if "mounts" not in self._config["disks"]:
        self._config["disks"]["mounts"] = ["/"]

      mounts = self._config["disks"]["mounts"]
      n_disks = len(mounts)
      return {"label": [f"{mnt}:" for mnt in mounts],
              "format": ["{0:.1f}%"]*n_disks,
              "range": [(0,100)]*n_disks,
              "colors": [
                (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),)
                ]*n_disks
              }
    else:
      return [psutil.disk_usage(mnt).percent
              for mnt in self._config["disks"]["mounts"]]
