Small System Performance-Monitor
================================

This project implements a plugable performance monitor for PCs.
The datacollector is a small Python script running on the PC collecting
data and sending them using UART over USB. The monitor itself is a
microcontroller (e.g. Raspberry Pi Pico) with an attached display. The
MCU reads the data from the serial connection and does all the
presentation work.

![](./waveshare-rp2040-geek.jpg)


PC-Installation
---------------

As a prerequisite the datacollector-script needs the Python package
`psutil` to collect performance data like free memory, disk space or
CPU-temperature. Install this package either using your
package-manager or with pip.

Afterwards, if you are running Linux, use:

    git clone https://github.com/bablokb/cp-sysmon
    cd cp-sysmon
    sudo pc/tools/install

to install the datacollector, an udev-rule and a systemd-service. The latter
two are not strictly necessary, but they automatically start the
PC-script whenever a suitable MCU is plugged in. The script is copied
to `/usr/local/bin/cp_sysmon.py`, the udev-rule to
`/etc/udev/rules.d/99-cp_sysmon.rules` and the systemd-service to
`/etc/systemd/system/cp_sysmon@.service`.


PC-Configuration
----------------

The configuration file for cp-sysmon is `/etc/cp_sysmon.json`. The install
routine above creates a default version:

```
{
  "#1": [
     "Unknown keys are ignored and treated as comments",
     "This json-file reproduces the defaults."
       ],
  "DEBUG": false,
  "INTERVAL": 1.5,
  "SENSORS": ["cpu", "freq", "temp", "mem"],
  "#2": [
     "sensors with specific configs need a dict",
     "with the same name as the sensor"
       ],
  "temp": {
    "#": "name and label depend on the system and must be changed",
    "name": "thinkpad",
    "label": "CPU"
    },
  "disks": {
    "#": [
      "'mounts' depends on preferences. Must be a list,",
      "Note that the SENSORS configuration does not contain 'disks' by default"
        ],
    "mounts": ["/"]
    },
}
```

Details about available sensors and on how to configure them are in
the file [`pc-config.md`](./pc-config.md).


Configuring Automatic Start
---------------------------

Besides the data collecter script, you should also update the udev-rule
installed by the install-script. This rule automatically starts the
collector script, but only if the correct device is plugged in. The
rule selects the device by serial-number. To query the serial number of
your device, run

    sudo udevadm monitor -s tty --environment

then plugin your device and scan the output for "ID_SERIAL_SHORT". Replace
the serial-id in `/etc/udev/rules.d/99-cpsysmon.rules`:

    KERNEL=="ttyACM*", SUBSYSTEM=="tty", ACTION=="add", ENV{ID_SERIAL_SHORT}=="DE62A87557822C2A",ENV{ID_USB_INTERFACE_NUM}=="02", RUN+="/bin/systemctl --no-block start cp_sysmon@$kernel.service"

Note that a manual execution of the collector script is always possible.
It starts and waits until the serial device passed as an argument shows up.


MCU-Installation
----------------

For the MCU, you need a device with native USB, e.g. a Pico or an ESP32-S3.
Install the current CircuitPython firmware from <https://circuitpython.org>.

Then copy all all files below `mcu` to your device. Additionally, you should
install the following libraries:

    - adafruit_display_text
    - adafruit_display_shapes
    - adafruit_bitmap_font
    - adafruit_ticks
    - a suitable display driver, e.g. adafruit_st7789

The tool `circup` (installable via pip) is the recommended way of installing
these libraries, e.g.:

    sudo apt-get -y install pip3
    pip3 install circup
    circup --path /path/to/device install -r requirements.txt


MCU-Configuration
-----------------

You need to configure some basic settings and the display driver for
the display that is attached to the MCU. `main.py` reads the
configuration from `config.py`. Copy one of the existing examples
`mcu/config_*` to `mcu/config.py` and adapt the settings and the
driver for your needs.

The file `mcu/config_st7789_240x135.py` is for the Waveshare
RP2040-Geek (with integrated Pico and ST7789 display), see the image
above. The file `mcu/config_waveshare_res_touch_28.py` is for the
Waveshare Res-Touch-LCD-2.8". This display has sockets for a Pico
underneath.

![](./waveshare-res-touch-lcd-2.8.jpg)

As this display is quiete large, it would be suitable to display more
data.


Hacking
-------

The current implementation only collects a few core performance
endpoints. You can change the collector to collect and display more
values. On MCU side, there should be nothing to do.

All endpoints (sensors) are defined within
[`pc/files/usr/local/bin/sysmon_sensors.py`](pc/files/usr/local/bin/sysmon_sensors.py). Use one of the existing sensors as a blueprint.

Another option would be to add data-logging. Many displays already have
an integrated SD-card slot, so besides live display of performance data
the system could also log them to a SD-card. This is not implemented yet,
pull requests are welcome. For performance reasons data-logging is best
done directly on the host though.
