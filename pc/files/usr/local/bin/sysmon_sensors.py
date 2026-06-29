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
    cfg["UI_CONFIG"] = {}
    cfg["UI_CONFIG"]["labels"]  = self._flatten(labels)
    cfg["UI_CONFIG"]["formats"] = self._flatten(formats)
    cfg["UI_CONFIG"]["ranges"]  = self._flatten(ranges)
    cfg["UI_CONFIG"]["colors"]  = self._flatten(colors)

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
      if "cpu_detail" not in self._config:
        self._config["cpu_detail"] = {}
      if "categories" not in self._config["cpu_detail"]:
        self._config["cpu_detail"]["categories"] = [
          "user", "system", "idle", "iowait"]
      categories = self._config["cpu_detail"]["categories"]
      n_cats = len(categories)
      def_colors = {
        "user": (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),),
        "nice": (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),),
        "system": (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),),
        "idle": (("0xFF0000",10),("0xFFFF00",20),("0x008000",None),),
        "iowait": (("0x008000",5),("0xFFFF00",15),("0xFF0000",None),),
        "irq": (("0x008000",5),("0xFFFF00",15),("0xFF0000",None),),
        "softirq": (("0x008000",5),("0xFFFF00",15),("0xFF0000",None),),
        "steal": (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),),
        "guest": (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),),
        "guest_nice": (("0x008000",70),("0xFFFF00",85),("0xFF0000",None),)
        }
      return {"label": [cat for cat in categories],
              "format": ["{0:.1f}%"]*n_cats,
              "range":  [(0,100)]*n_cats,
              "colors": [def_colors[cat] for cat in categories]
              }
    else:
      cpu_time_percent = psutil.cpu_times_percent()
      return [getattr(cpu_time_percent,cat,0)
              for cat in self._config["cpu_detail"]["categories"]]

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
      n_cpus = psutil.cpu_count()
      return {"label": ["L 1m:", "L 5m:","L 15m:",],
              "format": ["{0:.2f}"]*3,
              "range": [(0,3*n_cpus)]*3,
              "colors": [(("0x008000",n_cpus),
                          ("0xFFFF00",1.5*n_cpus),("0xFF0000",None),)]*3
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
