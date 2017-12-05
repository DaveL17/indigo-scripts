#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

""""
A script for creating animated graphics based on the ImageMagick library.

The script below is more of a proof of concept or a how-to. If you know Python,
it is easy to adapt it for use with Indigo. Note that this script requires
ImageMagick to be installed on the server machine. ImageMagick is not a part
of the base Python installation.

https://wiki.python.org/moin/ImageMagick
"""

import subprocess

work_fldr = "/Library/Application\ Support/Perceptive\ Automation/Indigo\ 7/IndigoWebServer/images/controls/static/"  # Spaces must be escaped

text_list = ['Upstairs Thermostat: 70°', 'Downstairs Thermostat: 68°', 'Outside Temperature: 68°', 'Uptime: 7 days, 12:38 [20:45]']

# First part of the output command string
output_cmd = "/opt/local/bin/convert -delay 400 -size 200x27 "

# Iterate through the items in the text list
for num in range(1, len(text_list) + 1):
    # Create a frame image based on the text list item and enumerate the filename
    proc = subprocess.Popen("/opt/local/bin/convert {0}bar.png -font arial -fill black -pointsize 12 -annotate +10+17 '{1}' {0}bar_frame{2}.gif".format(work_fldr, text_list[num - 1], num), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # print(proc.communicate())

    # Add command to the output command string for the new frame
    output_cmd += "-page +0+0 {0}bar_frame{1}.gif ".format(work_fldr, num)

# The last part of the output command string
output_cmd += "-loop 0 {0}bar_animation.gif".format(work_fldr)

proc1 = subprocess.Popen(output_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
# print(proc1.communicate())
