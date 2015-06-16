#!/usr/bin/env python
"""
You can precisely layout text in data or axes (0,1) coordinates.  This
example shows you some of the alignment and rotation specifications to
layout text
"""

from pylab import *
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

#ion()

# build a rectangle in axes coords
left, width = 0, 1.0
bottom, height = 0, 1.0
right = left + width
top = bottom + height
ax = gca()
p = Rectangle((left, bottom), width, height,
              fill=False,
              )
p.set_transform(ax.transAxes)
p.set_clip_on(False)
ax.add_patch(p)

f = gcf()
fig_size = f.get_size_inches()
print "Size in Inches", fig_size
dpi = f.get_dpi()
print "dpi", dpi
axis('off')

for index in range(1,49):

    text = ax.text(0.5*(left+right), 0.5*(bottom+top), index,
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes, fontsize=96)

    savefig('{:02d}.jpg'.format(index), dpi=64)
    text.remove()

#raw_input("Enter to quit")
