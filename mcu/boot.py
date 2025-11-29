# ----------------------------------------------------------------------------
# Show system statistics using DataBars.
#
# Configure USB-CDC during boot.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import usb_cdc
usb_cdc.enable(data=True)   # enable second (binary) UART over USB
