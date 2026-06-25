# ----------------------------------------------------------------------------
# sensors.py: collection of data-sampling wrappers.
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

  # --- multiplexer   --------------------------------------------------------

  def get_data(self, sensor):
    """ return data for the given sensor """

    return getattr(self,f"_{sensor}",self._not_implemented)(sensor)

  # --- fallback method, raises exception   ----------------------------------

  def _not_implemented(self, sensor):
    """ raises error if there is no implementation for sensor """
    raise ValueError(f"error: sensor {sensor} is not implemented!")

  # --- return cpu percent   -------------------------------------------------

  def _cpu(self, _):
    """ return CPU """
    return [psutil.cpu_percent()]

  # --- return detailed cpu usage   ------------------------------------------

  def _cpu_detail(self, _):
    """ return CPU-details for info in
    [user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice]
    """
    cpu_time_percent = psutil.cpu_times_percent()
    return [getattr(cpu_time_percent,info,0) for
            for info in self._config["CPU_DETAILS"]]

  # --- return cpu frequency   -----------------------------------------------

  def _freq(self, _):
    """ return CPU frequency """
    return [psutil.cpu_freq().current]

  # --- return cpu load   ----------------------------------------------------

  def _load(self, _):
    """ return CPU load """
    return [load for load in psutil.getloadavg()]

  # --- return system temperature   ------------------------------------------

  def _temp(self, _):
  """ return system temperature """
  try:
    name, label = self._config["TEMP"]
    component = psutil.sensors_temperatures()[name]
    for value in component:
      if value.label == label:
        return [int(round(value.current,0))]
    return [0]
  except:
    return [0]

  # --- return memory usage   ------------------------------------------------

  def _mem(self, _):
    """ return memory usage """
    return [psutil.virtual_memory().percent]

  # --- return used disk-space   ---------------------------------------------

  def _disks(self, _):
    """ return used disk-space """
    return [psutil.disk_usage(mnt).percent
            for mnt in self._config["DISK_MOUNTS"]]
