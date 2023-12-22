#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D Map Planar v1.0

Note: this script requires Python 3.x
"""

# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle  # PathPatch
# from matplotlib.text import TextPath
# from matplotlib.transforms import Affine2D
from mpl_toolkits.mplot3d import art3d
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
# from matplotlib import animation
# import sys


# ==============================================================================
def animate(frame):
    """
    Animation function

    :param frame:
    :return:
    """
    ax.view_init(elev=30, azim=frame / 4)
    plt.pause(interval=.001)
    return fig


# ==============================================================================
def draw_room(origin, w, h, lvl, obs):

    # Draw rectangle
    room = Rectangle(origin, width=w, height=h, color=cmap(norm(obs)), ec='k', lw=.3, alpha=.4)
    ax.add_patch(room)
    art3d.pathpatch_2d_to_3d(room, z=lvl, zdir="z")


# data = sys.argv[1]

fig = plt.figure()
ax = fig.gca(projection='3d')

# ================================= Color Map ==================================
# Matplotlib color map
# see: https://matplotlib.org/stable/gallery/color/colormap_reference.html
#      https://matplotlib.org/stable/gallery/color/custom_cmap.html
# lower <---> higher
# Temperature: bwr (blue, white, red)
# Humidity: Blues (white, blue)
cmap = plt.cm.bwr
norm = Normalize(vmin=50, vmax=80)

# ============================== Room Coordinates ==============================
# Lower Level
draw_room(origin=(26, 15), w=24, h=30, lvl=1, obs=62)  # basement
draw_room(origin=(50, 15), w=14, h=30, lvl=1, obs=58)  # workshop

# First Floor
draw_room(origin=(26, 32), w=13, h=16, lvl=2, obs=67)  # dining room
draw_room(origin=(39, 15), w=11, h=15, lvl=2, obs=67)  # foyer down
draw_room(origin=(2, 22), w=24, h=22, lvl=2, obs=56)  # garage
draw_room(origin=(39, 30), w=11, h=21, lvl=2, obs=68)  # kitchen
draw_room(origin=(26, 25), w=6, h=7, lvl=2, obs=68)  # laundry
draw_room(origin=(50, 15), w=14, h=30, lvl=2, obs=68)  # living room
draw_room(origin=(26, 15), w=13, h=10, lvl=2, obs=69)  # parlor
draw_room(origin=(32, 25), w=7, h=7, lvl=2, obs=68)  # powder room

# Second Floor
draw_room(origin=(39, 15), w=11, h=20, lvl=3, obs=71)  # foyer up
draw_room(origin=(39, 35), w=11, h=17, lvl=3, obs=67)  # master bath
draw_room(origin=(50, 15), w=14, h=23, lvl=3, obs=71)  # master bedroom
draw_room(origin=(50, 38), w=14, h=8, lvl=3, obs=68)  # master closet
draw_room(origin=(26, 27), w=13, h=8, lvl=3, obs=68)  # guest bath
draw_room(origin=(26, 35), w=13, h=14, lvl=3, obs=68)  # guest bedroom
draw_room(origin=(26, 15), w=13, h=12, lvl=3, obs=68)  # office

# Attics
draw_room(origin=(2, 22), w=24, h=22, lvl=3, obs=65)  # garage attic
draw_room(origin=(26, 15), w=38, h=38, lvl=4, obs=75)  # main attic

# ================================= Occupancy ==================================
# This is the occupancy point (as an example). Plot point at middle of room dimension:
# (50% of x dimension, 50% of y, 50% of z -- of _room_)
# ax.scatter(57, 30, 1, fc='r', s=10)  # Workshop

# ============================== Plot Parameters ===============================
ax.set_xlabel('')
ax.set_xlim(0, 70)
ax.set_xticklabels([])
ax.xaxis.set_pane_color((1, 1, 1, 1))

ax.set_ylabel('')
ax.set_ylim(0, 70)
ax.set_yticklabels([])
ax.yaxis.set_pane_color((1, 1, 1, 1))

ax.set_zlabel('Floor')
ax.set_zlim(1, 4)
ax.set_zticks([1, 2, 3, 4])
ax.zaxis.set_pane_color((1, 1, 1, 1))
ax.set_zticklabels(['Bsmt', '1st', '2nd', 'Attic'])

# ================================== Animate ===================================
# Animate the plot and save it to disk. Requires ffmpeg (or alternative backend) to be installed.
# Writer = animation.writers['ffmpeg']
# writer = Writer(fps=60, metadata=dict(artist='Me', title='3D Temperature Map'), bitrate=1800)
# ani = animation.FuncAnimation(fig, animate, frames=1500, interval=24, repeat=True)
# ani.save('/Users/Dave/Temp/anim_24_1500_60fps_planar.mp4')

# plt.show()
plt.savefig('/Users/Dave/Temp/Figure 1.png')
