#! /usr/bin/env python
# -*- coding: utf-8 -*-

""""
A script for creating animated graphics based on the ImageMagick library.

The script below is more of a proof of concept or a how-to. If you know Python,
it is easy to adapt it for use with Indigo. Note that this script requires
ImageMagick to be installed on the server machine. ImageMagick is not a part
of the base Python installation, so you'll need to install it to a place that
Indigo can see.

https://wiki.python.org/moin/ImageMagick
"""

import subprocess

# Where the image will reside.  Spaces must be escaped.
work_fldr = "/Library/Application Support/Perceptive Automation/Indigo 2022.1/Web Assets/images/controls/static"

# Change this list to device states, variable values, etc. Can be string, int, float, etc.
text_list = ["Upstairs Thermostat: 70°", "Downstairs Thermostat: 68°", "Outside Temperature: 68°", "Up Time: 7 days, 12:38 [20:45]", 1.23]

# First part of the output command string
output_cmd = "/opt/local/bin/convert -delay 300 -size 200x27 "

# Iterate through the items in the text list to create a frame image based on
# the text list item and enumerate the filename.
for num in range(1, len(text_list) + 1):
    # Build each frame image +h+v
    proc = subprocess.Popen("/opt/local/bin/convert {0}bar.png -font arial -fill black -pointsize 12 -annotate +10+17 '{1}' "
                            "{0}bar_frame{2}.gif".format(work_fldr, text_list[num - 1], num), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # For debugging, you can look at the shell's return.
    # print(proc.communicate())

    # Add command to the output command string for the new frame image
    output_cmd += "-page +0+0 {0}bar_frame{1}.gif ".format(work_fldr, num)

# The last part of the output command string
output_cmd += "-loop 0 {0}bar_animation.gif".format(work_fldr)

# Build the animation.
proc1 = subprocess.Popen(output_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

# For debugging, you can look at the shell's return.
# print(proc1.communicate())
