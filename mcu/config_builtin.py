# ----------------------------------------------------------------------------
# Configuration settings for a device with integrated display.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

import board
from dataviews.Base import Color

# --- basic configuration (optional)   ---------------------------------------

#FONT      = "fonts/DejaVuSans-16-subset.bdf"
#BG_COLOR  = Color.BLACK
#TXT_COLOR = Color.AQUA
#BORDER    = 1
#PADDING   = 3
#DIVIDER   = 1
#BAR_WIDTH   = 3/4 of display width
#BAR_HEIGHT  = display height divided by n_stats minus border/divider/padding

#DATA_SOURCE = 'usb'  # 'usb' or tuple (rx-pin,tx-pin)

# --- display creation   ------------------------------------------------------

display = board.DISPLAY
