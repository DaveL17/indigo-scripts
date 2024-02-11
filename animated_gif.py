#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A script for creating animated graphics based on the ImageMagick library.

The script below is more of a proof of concept or a how-to. If you know Python, it is easy to adapt it for use with
Indigo. Note that this script requires ImageMagick to be installed on the server machine. ImageMagick is not a part of
the base Python installation, so you'll need to install it to a place that Indigo can see.

https://wiki.python.org/moin/ImageMagick
"""

import subprocess
try:
    import indigo
except ImportError:
    pass

# Where the image will reside.  Spaces must be escaped.
IMAGES_FILE_PATH = "/Web Assets/images/controls/static/battery_test.png"
work_fldr = indigo.server.getInstallFolderPath() + IMAGES_FILE_PATH

# Change this list to device states, variable values, etc. Can be string, int, float, etc.
text_list = ["Upstairs Thermostat: 70°",
             "Downstairs Thermostat: 68°",
             "Outside Temperature: 68°",
             "Up Time: 7 days, 12:38 [20:45]",
             1.23
             ]

# First part of the output command string
OUTPUT_CMD = "/opt/local/bin/convert -delay 300 -size 200x27 "

# Iterate through the items in the text list to create a frame image based on the text list item and enumerate the
# filename.
for num in range(1, len(text_list) + 1):
    # Build each frame image +h+v
    with subprocess.Popen(f"/opt/local/bin/convert {work_fldr}bar.png -font arial -fill black -pointsize 12 "
                          f"-annotate +10+17 '{ text_list[num - 1]}' {work_fldr}bar_frame{num}.gif",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                          ) as proc:

        # For debugging, you can look at the shell's return.
        print(proc.communicate())

    # Add command to the output command string for the new frame image
    OUTPUT_CMD += f"-page +0+0 {work_fldr}bar_frame{num}.gif "

# The last part of the output command string
OUTPUT_CMD += f"-loop 0 {work_fldr}bar_animation.gif"

# Build the animation.
with subprocess.Popen(OUTPUT_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as proc1:
    # For debugging, you can look at the shell's return.
    print(proc1.communicate())
