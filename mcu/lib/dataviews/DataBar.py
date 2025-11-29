# ----------------------------------------------------------------------------
# DataBar: This class displays data as horizontal or vertical bar.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-dataviews
# ----------------------------------------------------------------------------

from vectorio import Rectangle
import gc
import displayio

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

from dataviews.Base import Justify
from .DataCell import DataCell

# --- Class implementing bars as cell-content   ------------------------------

class DataBar(DataCell):

  # --- constructor   --------------------------------------------------------

  def __init__(self,size, font, color, bg_color=None, format=None,
               text_justify=Justify.LEFT, text_color=None,
               horizontal=True, range=(0,100)):
    """ constructor """

    if font:
      if isinstance(font,str):
        font = bitmap_font.load_font(font)

    super().__init__(font,color,bg_color,format)
    self._size       = size
    self._justify    = text_justify
    self._range      = range
    self._horizontal = horizontal

    self._palette = displayio.Palette(2)
    self._palette[0] = bg_color
    if isinstance(color,(list,tuple)):
      self._palette[1] = color[0][0]
    else:
      self._palette[1] = color
    self._text_color = self._palette[1] if text_color is None else text_color

    # horizontal: size=(max_hsize,vsize).
    # vertical: size=(hsize,max_vsize).
    # initial variable dimension is zero.
    self._set_size(None)

    # initial content is an empty group
    self.content = displayio.Group()

  # --- calculate size from value   ------------------------------------------

  def _set_size(self,value):
    """ calculate size from value """

    # no values, no size
    if value is None:
      if self._horizontal:
        self.width  = 0
        self.height = self._size[1]    # will be constant
      else:
        self.width  = self._size[0]    # will be constant
        self.height = 0
      return

    # otherwise, calculate fractional size of the bar
    rel_size = max(0,min(
      (value-self._range[0])/(self._range[1]-self._range[0]),1))
    if self._horizontal:
      self.width = int(rel_size*self._size[0])
    else:
      self.height = int(rel_size*self._size[1])

  # --- set position   -------------------------------------------------------

  def set_position(self,anchor_point,anchor_position):
    """ set position of content """

    if not len(self.content):
      return
    else:
      self.content.x = int(anchor_position[0]
                           - round(anchor_point[0] * self.width)
                           )
      self.content.y = int(anchor_position[1]
                           - round(anchor_point[1] * self.height)
                           )

  # --- set color   ----------------------------------------------------------

  def set_color(self,color):
    """ set color """
    super().set_color(color)
    self._palette[1] = self.value2color(self.value)

  # --- get label   -----------------------------------------------------------

  def _get_label(self):
    """ create label for value """

    lbl = label.Label(self.font,
                      color=self._text_color,
                      text=self.format.format(self.value))

    if self._justify == Justify.LEFT:
      # start of bar
      x = self.content[0].x
    elif self._justify == Justify.RIGHT:
      # end of bar, using max-size
      x = max(self._size[0],self.width)
    else:
      # center of bar
      x = 0.5*(self.width-self.content[0].x)

    x_anchor = 0.5*self._justify
    y        = self.height/2

    lbl.anchor_point = (x_anchor,0.5)
    lbl.anchored_position = (x,y)
    return lbl

  # --- set value   -----------------------------------------------------------

  def set_value(self,value):
    """ set value of content """

    super().set_value(value)
    self._set_size(value)

    if value is None or self.height == 0:
      for i in range(len(self.content)):
        self.content.pop()
      gc.collect()
      return

    self._palette[1] = self.value2color(value)
    if self.width:
      bar = Rectangle(x=0,y=0,
                      pixel_shader=self._palette,
                      width=self.width,
                      height=self.height,
                      color_index=1)
    else:
      bar = displayio.Group()       # dummy content
    if len(self.content):
      # content already available
      self.content[0] = bar
    else:
      self.content.append(bar)

    if self.format:
      if len(self.content) == 2:
        # label already available
        self.content[1] = self._get_label()
      else:
        self.content.append(self._get_label())
    gc.collect()

  # --- invert color   -------------------------------------------------------

  def invert(self):
    """ swap color and bg_color """
    super().invert()
    self._palette[1] = self.value2color(self.value)
