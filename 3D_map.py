#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D Map v1.2

Creates a 3D polygon chart. THe example code creates a map of a home and shows how you can color the polygons for
temperature or humidity using a color map.

Note: this script requires Python 3.x and, if saving animation to disk, ffmpeg.
"""

# import sys  # uncomment if using the sys.argv statement below
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import Normalize
# from matplotlib import animation  # uncomment if using the animation code below


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
def plot_shape(coords, obs):
    """
    Plot all sides of each polygon
    Credit: https://stackoverflow.com/a/49766400/2827397

    :param coords:
    :param obs:
    :return:
    """

    definition_array = [np.array(list(item)) for item in coords]

    points = []
    points += definition_array

    vectors = [definition_array[1] - definition_array[0],
               definition_array[2] - definition_array[0],
               definition_array[3] - definition_array[0]
               ]

    points += [definition_array[0] + vectors[0] + vectors[1]]
    points += [definition_array[0] + vectors[0] + vectors[2]]
    points += [definition_array[0] + vectors[1] + vectors[2]]
    points += [definition_array[0] + vectors[0] + vectors[1] + vectors[2]]

    points = np.array(points)

    edges = [[points[0], points[3], points[5], points[1]],
             [points[1], points[5], points[7], points[4]],
             [points[4], points[2], points[6], points[7]],
             [points[2], points[6], points[3], points[0]],
             [points[0], points[2], points[4], points[1]],
             [points[3], points[6], points[7], points[5]]
             ]

    faces = Poly3DCollection(edges, lw=.3, ec='k', fc=cmap(norm(obs)), alpha=.2)
    ax.add_collection3d(faces)

    # Plot the points themselves to force the scaling of the axes. We set their size to zero, so they are invisible.
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=0)

    ax.set_aspect('auto')


# data = sys.argv[1]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# ================================= Color Map ==================================
# see: https://matplotlib.org/stable/gallery/color/colormap_reference.html
#      https://matplotlib.org/stable/gallery/color/custom_cmap.html
# lower <---> higher
# Temperature: `bwr` (blue, white, red)
# Humidity: `Blues` (white, blue)
cmap = plt.cm.bwr
norm = Normalize(vmin=50, vmax=80)

# ============================== Room Coordinates ==============================
# Coordinates: [(x, y, z origin),
#               (x length, y origin, z origin),
#               (x origin, y length, z origin),
#               (x origin, y origin, z height)
#               ]

# Lower Level
plot_shape(coords=[(24, 20, 0), (48, 20, 0), (24, 50, 0), (24, 20, 10)], obs=62)  # basement
plot_shape(coords=[(48, 20, 0), (62, 20, 0), (48, 50, 0), (48, 20, 10)], obs=58)  # workshop

# First Floor
plot_shape(coords=[(24, 35, 10), (37, 35, 10), (24, 50, 10), (24, 35, 18)], obs=67)  # dining room
plot_shape(coords=[(0, 24, 10), (24, 24, 10), (0, 48, 10), (0, 24, 20)], obs=56)     # garage
plot_shape(coords=[(37, 20, 10), (48, 20, 10), (37, 35, 10), (37, 20, 18)], obs=67)  # foyer down
plot_shape(coords=[(37, 35, 10), (48, 35, 10), (37, 50, 10), (37, 35, 18)], obs=68)  # kitchen
plot_shape(coords=[(24, 30, 10), (30, 30, 10), (24, 35, 10), (24, 30, 18)], obs=68)  # laundry
plot_shape(coords=[(48, 20, 10), (62, 20, 10), (48, 50, 10), (48, 20, 18)], obs=68)  # living room
plot_shape(coords=[(24, 20, 10), (37, 20, 10), (24, 30, 10), (24, 20, 18)], obs=69)  # parlor
plot_shape(coords=[(30, 30, 10), (37, 30, 10), (30, 35, 10), (30, 30, 18)], obs=68)  # powder

# Second Floor
plot_shape(coords=[(37, 20, 18), (48, 20, 18), (37, 35, 18), (37, 20, 26)], obs=71)  # foyer up
plot_shape(coords=[(24, 35, 18), (37, 35, 18), (24, 50, 18), (24, 35, 26)], obs=68)  # guest br
plot_shape(coords=[(24, 30, 18), (37, 30, 18), (24, 35, 18), (24, 30, 26)], obs=68)  # guest bath
plot_shape(coords=[(37, 35, 18), (48, 35, 18), (37, 50, 18), (37, 35, 26)], obs=67)  # master bath
plot_shape(coords=[(48, 20, 18), (62, 20, 18), (48, 42, 18), (48, 20, 26)], obs=71)  # master br
plot_shape(coords=[(48, 42, 18), (62, 42, 18), (48, 50, 18), (48, 42, 26)], obs=68)  # master closet
plot_shape(coords=[(24, 20, 18), (37, 20, 18), (24, 30, 18), (24, 20, 26)], obs=68)  # office

# Attics
plot_shape(coords=[(0, 24, 20), (24, 24, 20), (0, 48, 20), (0, 24, 30)], obs=65)  # garage attic
plot_shape(coords=[(24, 20, 26), (62, 20, 26), (24, 50, 26), (24, 20, 36)], obs=75)  # main attic

# ================================= Occupancy ==================================
# This is the occupancy point (as an example). Plot point at middle of room dimension:
# (50% of x dimension, 50% of y, 50% of z -- of _room_)
# ax.scatter(55, 35, 5, fc='r', s=10)  # Workshop

# ============================== Plot Parameters ===============================
ax.set_xlabel('')
ax.set_xlim(0, 70)
ax.set_xticklabels([])
ax.xaxis.set_pane_color((1, 1, 1, 1))

ax.set_ylabel('')
ax.set_ylim(0, 70)
ax.set_yticklabels([])
ax.yaxis.set_pane_color((1, 1, 1, 1))

ax.set_zlabel('')
ax.set_zlim(0, 70)
ax.set_zticks([5, 14, 22, 31, 40, 50, 60, 70])
ax.set_zticklabels(['', '', '', '', '', '', '', ''])
ax.zaxis.set_pane_color((1, 1, 1, 1))

# ================================== Animate ===================================
# Animate the plot and save it to disk. Requires ffmpeg (or alternative backend) to be installed.
# Writer = animation.writers['ffmpeg']
# writer = Writer(fps=60, metadata=dict(artist='Me', title='3D Temperature Map'), bitrate=1800)
# ani = animation.FuncAnimation(fig, animate, frames=1500, interval=24, repeat=True)
# ani.save('/Users/Dave/Temp/anim_24_1500_60fps.mp4')

# plt.show()
plt.savefig('/Users/Dave/Temp/Figure 1 Planar.png')
