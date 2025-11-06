#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A script for creating animated graphics based on the ImageMagick library.
"""

import subprocess

try:
    import indigo  # noqa
except ImportError:
    pass

# Where the image will reside.
IMAGES_FILE_PATH = "/Web Assets/images/controls/static/"
work_fldr = indigo.server.getInstallFolderPath() + IMAGES_FILE_PATH
# Change this list to device states, variable values, etc.
text_list = [
    "Upstairs Thermostat: 70°",
    "Downstairs Thermostat: 68°",
    "Outside Temperature: 68°",
    "Up Time: 7 days, 12:38 [20:45]",
    1.23,
]

# First part of the output command string
OUTPUT_CMD = "magick -delay 300 -size 200x27 "

# Iterate through the items in the text list
for num in range(1, len(text_list) + 1):
    # Build each frame image - NOTE: Added quotes around file paths
    cmd = (
        f'magick "{work_fldr}bar.png" -font arial -fill black -pointsize 12 '
        f'-annotate +10+17 "{text_list[num - 1]}" "{work_fldr}bar_frame{num}.gif"'
    )

    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    ) as proc:
        indigo.server.log(f"{proc.communicate()}")

    # Add command to the output command string for the new frame image
    OUTPUT_CMD += f'-page +0+0 "{work_fldr}bar_frame{num}.gif" '

# The last part of the output command string
OUTPUT_CMD += f'-loop 0 "{work_fldr}bar_animation.gif"'

# Build the animation.
with subprocess.Popen(
    OUTPUT_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
) as proc1:
    indigo.server.log(f"{proc1.communicate()}")
