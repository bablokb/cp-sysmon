Configuration of the Datacollector
==================================


Overview
--------

The datacollector `/usr/local/bin/cp_sysmon.py` tries to read the
optional file `/etc/cp_sysmon.json` and merges configuration
information from there with the program internal defaults. Usually, it
is only necessary to change a few things like the sampling interval,
the list of sensors to to read and most notably how to query the
CPU/system temperature.

A minimal configuration example:

```
{
  "DEBUG": false,
  "INTERVAL": 1.5,
  "SENSORS": ["cpu", "freq", "temp", "mem"],
  "temp": {
    "name": "thinkpad",
    "label": "CPU"
    }
}
```


Global Settings
---------------

Following global settings are supported (all in capital letters):

  - `DEBUG`: `false|true`: print debug output
  - `BAUD`: `115200`. A valid baudrate for the serial line.
     Must match the MCU configuration
  - `INTERVAL`: `1.5`. See below for hints.
  - `SENSORS`: `["cpu", "freq", "temp", "mem"]`: List of sensors.

Currently implemented sensors (in lower case letters):

  - `cpu`: CPU usage as percent
  - `cpu_detail`: CPU usage details
  - `freq`: CPU frequency
  - `temp`: system (or CPU) temperature
  - `mem`: used memory in percent
  - `disks`: uses diskspace in percent
  - `load`: system load

Some sensors need a specific configuration. Use a top-level dict with
the sensor name as the key. Details for the sensors are documented below.


INTERVAL
--------

The `INTERVAL` value defines the data-sampling interval.  Sampling
data faster than the MCU is able to process them will result in a
delayed view of the measurements. You can set `DEBUG=True` within
`config.py` of the MCU to print the update speed of the MCU. A Pico
(RP2040) with attached ST7789 display can do an update about every 0.8
seconds (this also depends on screen-size and how many values have to
be displayed).

Since there is a delay at startup while the MCU initializes the
display, you should use a value that is higher, or else the MCU will
never catch up. For example with `INTERVAL=1` it takes about 25s until
the MCU shows live data.

You should also keep in mind that short intervals also keep the PC
busy. So sampling as fast as the MCU can process the data is also not
the best idea, especially in high load situations.


cpu_datail
----------

This sensor has a number of endpoints (categories), some of which might
not be necessary. To configure the list of categories, use:

```
"cpu_detail": {
   "categories": [
       "user", "nice", "system", "idle", "iowait", "irq",
        "softirq", "steal", "guest", "guest_nice"
       ]
 }
 ```

The default value of `categories` is `["user", "system", "idle", "iowait"]`.


temp
----

Reading the CPU/system temperature is complicated, since the physical
system has many different components that provide temperature
readings. The correct value is keyed by a "name" and a "label":

```
"temp": {
  "name": "thinkpad",
  "label": "CPU"
}
```
To detect the correct name of the component and the corresponding
label, run:

    python3
    >>> import psutil
    >>> psutil.sensors_temperature()

The output is not very readable but you should identify various components
of your PC, e.g. NVMe disks, PCIe bridges or the system itself. Check
which component and label is most suitable and configure the `temp`-dict
accordingly.


disks
-----

Information about free disk-space is available by disk-mount. To configure
the mounts to report, add a dict with:

```
"disks": {
  "mounts": ["/", "/home"]
  },
```


UI Settings
-----------

For every sensor the configuration file can override any of four
attributes that are relevant for the rendering of the results:

  - `label`: the labels to display
  - `format`: the format to use
  - `ranges`: the expected ranges of the values
  - `colors`: a list of subranges that map the subrange to a specific color

All four attributes can have scalar or lists as values. Sensors like
`cpu` need a scalar, while sensors like `disks` need a list. All
overriden attributes need to have the same shape, e.g. if you monitor
three mount-points with the `disks`-sensor you need a list of three
labels, ranges and colors.

Normally, overriding the defaults is not necessary, but there are use cases
where this is sensible.

Example:

```
"cpu": {
  "format": "{0:.2f}%",
  "colors": [["0x88E788",20],["0x008000",70],["0xFFFF00",85],["0xFF0000",null]]
}

```

This example changes the default format (with two digits instead of
one digit after the decimal) and adds an additional color (light-green)
to the color mapping for cpu-values below 20%. Values above 20% to 70%
are green, values up to 85% are yellow and values above 85% are red.

Note that in the example the `colors` attribute is technically a list,
but it is a logical scalar in the sense that it is a single
color-map. Changing the colors for multi-dimensional endpoints must
provide a list of color-maps.
