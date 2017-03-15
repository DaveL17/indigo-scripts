#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import subprocess

# Note that this script requires ImageMagick to be installed on the server machine
output_fldr = "/Library/Application\ Support/Perceptive\ Automation/Indigo\ 6/IndigoWebServer/images/controls/static/"  # Spaces must be escaped
work_fldr = "/Users/username/Desktop/"

text_list = ['Upstairs Thermostat: 70°', 'Downstairs Thermostat: 68°', 'Outside Temperature: 68°', 'Server Uptime: 7 days, 12:38 [20:45]']

# First part of the output command string
output_cmd = "/opt/local/bin/convert -delay 400 -size 500x100 "

# Iterate through the items in the text list
for num in range(1, len(text_list) + 1):
    # Create a frame image based on the text list item and enumerate the filename
    proc = subprocess.Popen("/opt/local/bin/convert {0}bar.png -font arial -fill white -pointsize 16 -annotate +40+55 '{1}' bar_frame{2}.gif".format(work_fldr, text_list[num - 1], num),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # Add command to the output command string for the new frame
    output_cmd += "-page +0+0 {0}bar_frame{1}.gif ".format(work_fldr, num)

# The last part of the output command string
output_cmd += "-loop 0 {0}bar_animation.gif".format(output_fldr)

proc = subprocess.Popen(output_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)