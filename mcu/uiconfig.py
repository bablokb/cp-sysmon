# ----------------------------------------------------------------------------
# UIConfig: helper class for UI configuration and view creation.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-sysmon
# ----------------------------------------------------------------------------

# Note: this is the default configuration. The connected host can override
#       this configuration. See the Readme for details.

import json
import gc

from dataviews.Base import Color, Justify
from dataviews.DataView  import DataView
from dataviews.DataPanel import DataPanel, PanelText
from dataviews.DataBar import DataBar

import config

class UIConfig:

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """
    self.labels  = ["CPU:",     "Mem:",     "Disk:",    "Temp:"],
    self.formats = ["{0:.1f}%", "{0:.1f}%", "{0:.1f}%", "{0}°C"],
    self.ranges  = [(0,100),    (0,100),    (0,100),    (35,85)],
    self.colors  = [
      [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
      [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
      [(Color.GREEN,70),(Color.YELLOW,85),(Color.RED,None)],
      [(Color.GREEN,65),(Color.YELLOW,80),(Color.RED,None)],
    ]
    self.n_bars = 4
    self.view = None

  # --- parse configuration read from serial   -------------------------------

  def parse(self, cfg):
    """ parse and update config """
    try:
      cfg = json.loads(cfg)
      self.n_bars  = len(cfg['labels'])
      self.formats = zip(cfg['labels'], cfg['formats'])
      self.ranges  = cfg['ranges']
      self.colors  = cfg['colors']
      self.view   = None                  # invalidate existing view
      gc.collect()
    except Exception as ex:
      print(f"failed to parse UI-configuration from serial (exception: {ex})")

   # --- create view   -------------------------------------------------------

   def create_view(self):
     """ (re-) create view """

     # create data-bars objects used in the DataView below
     n_bars = self.n_bars

     font       = getattr(config,"FONT","fonts/DejaVuSans-16-subset.bdf")
     bg_color   = getattr(config,"BG_COLOR", Color.BLACK)
     txt_color  = getattr(config,"TXT_COLOR", Color.AQUA)
     border     = getattr(config,"BORDER", 1)
     padding    = getattr(config,"PADDING", 3)
     divider    = getattr(config,"DEVIDER", 1)
     bar_width  = getattr(config,"BAR_WIDTH", int(0.75*config.display.width))
     bar_height = getattr(config,"BAR_HEIGHT",
                          int((config.display.height - 2*border -
                               (n_bars-1)*divider -
                               n_bars*2*padding)/n_bars
                              )
                          )

     bars = [None]*n_bars
     for i in range(n_bars):
       bars[i] = (0,2*i+1,DataBar(size=(bar_width, bar_height),
                                  range=self.ranges[i],
                                  format=self.formats[2*i+1],
                                  color=self.colors[i],
                                  text_color=txt_color,
                                  text_justify=Justify.RIGHT,
                                  font=font,
                                  bg_color=bg_color))

     # create view with n_bars rows (right align labels)
     self.view = DataView(
       dim=(n_bars,2),
       width=config.display.width,height=config.display.height,
       justify=Justify.RIGHT,
       fontname=font,
       formats=self.formats,
       border=border,
       divider=divider,
       padding=padding,
       bg_color=bg_color,
       col_width=[0,1],
       objects = bars
       )

     # left align hbars
     for index in range(1,2*n_bars,2):
       self.view.justify(Justify.LEFT,index=index)

     config.display.root_group = self.view
