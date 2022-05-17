#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a battery health chart for display in Indigo control pages
"""
from datetime import datetime

try:
    import sys
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    sys.exit("The matplotlib and numpy modules are required to use this script.")

# =================== User Settings ===================
output_file = indigo.server.getInstallFolderPath() + '/Web Assets/images/controls/static/battery_test.png'  # Indigo 2022.1 installs
today = datetime.now()

chart_title = 'Battery Health as of ' + today.strftime("%A %I:%M %p")

BACKGROUND_COLOR = '#000000'
BATTERY_CAUTION_COLOR = '#FFFF00'
BATTERY_CAUTION_LEVEL = 20
BATTERY_FULL_COLOR = '#0000CC'
BATTERY_LOW_COLOR = '#FF0000'
BATTERY_LOW_LEVEL = 10
CHART_HEIGHT = 4.5
CHART_WIDTH = 6
FONT_COLOR = '#FFFFFF'
FONT_NAME = 'Lato Light'
FONT_SIZE = 9
GRID_COLOR = '#888888'
GRID_STYLE = 'dotted'
SHOW_DATA_LABELS = True
TITLE_FONT_SIZE = 9
X_AXIS_TITLE = ''
Y_AXIS_TITLE = ''

# =================== kwarg Settings ===================
k_bar_fig = {
    'align': 'center',
    'alpha': 1.0,
    'height': 0.5,
    'zorder': 3
}

k_grid_fig = {
    'which': 'major',
    'color': GRID_COLOR,
    'linestyle': GRID_STYLE,
    'zorder': 0
}

k_plot_fig = {
    'bbox_extra_artists': None,
    'bbox_inches': 'tight',
    'dpi': 100,
    'edgecolor': BACKGROUND_COLOR,
    'facecolor': BACKGROUND_COLOR,
    'format': None,
    'frameon': None,
    'orientation': None,
    'pad_inches': 0.1,
    'papertype': None,
    'transparent': True,
}

k_title_fig = {
    'fontname': FONT_NAME,
    'fontsize': TITLE_FONT_SIZE,
    'color': FONT_COLOR,
    'position': (0.35, 1.0)
}

# =====================================================

bar_colors = []
device_dict = {}
x_values = []
y_values = []

# Create a dictionary of battery powered devices and their battery levels
try:
    for dev in indigo.devices.itervalues():
        if dev.batteryLevel is not None:
            device_dict[dev.name] = dev.states['batteryLevel']

    if not device_dict:
        device_dict['No Battery Devices'] = 0

except Exception as e:
    indigo.server.log(f"Error reading battery devices: {e}")

# Parse the battery device dictionary for plotting.
try:
    for key, value in sorted(device_dict.items(), key=lambda x: x[1], reverse=True):
        try:
            x_values.append(float(value))
        except ValueError:
            x_values.append(0)
        y_values.append(key.replace(' - ', '\n'))  # This line is specific to my install, as I name devices "Room - Device Name"

        # Create a list of colors for the bars based on battery health
        try:
            battery_level = float(value)
        except ValueError:
            battery_level = 0

        if battery_level <= BATTERY_LOW_LEVEL:
            bar_colors.append(BATTERY_LOW_COLOR)
        elif BATTERY_LOW_LEVEL < battery_level <= BATTERY_CAUTION_LEVEL:
            bar_colors.append(BATTERY_CAUTION_COLOR)
        else:
            bar_colors.append(BATTERY_FULL_COLOR)

except Exception as e:
    indigo.server.log(f"Error parsing chart data: {e}")

# Create a range of values to plot on the Y axis, since we can't plot on device names.
y_axis = np.arange(len(y_values))

# Plot the figure
plt.figure(figsize=(CHART_WIDTH, CHART_HEIGHT))

# Adding 1 to the y_axis pushes the bar to spot 1 instead of spot 0 -- getting it off the axis.
plt.barh((y_axis + 1), x_values, color=bar_colors, **k_bar_fig)

if SHOW_DATA_LABELS:
    for ii in range(len(y_axis)):
        plt.annotate(f"{x_values[ii]:3}", xy=((x_values[ii] - 5), (y_axis[ii]) + 0.88),
                     xycoords='data', textcoords='data', fontsize=FONT_SIZE, color=FONT_COLOR)

# Chart
plt.title(chart_title, **k_title_fig)
plt.grid(**k_grid_fig)

# X Axis
plt.xticks(fontsize=FONT_SIZE, color=FONT_COLOR)
plt.xlabel(X_AXIS_TITLE, fontsize=FONT_SIZE, color=FONT_COLOR)
plt.gca().xaxis.grid(True)
plt.xlim(xmin=0, xmax=100)

# Y Axis
# The addition of 0.05 to the y_axis better centers the labels on the bars (for 2-line labels.) For
# 1 line labels, change 1.05 to 1.0.
plt.yticks((y_axis + 1.05), y_values, fontsize=FONT_SIZE, color=FONT_COLOR)
plt.ylabel(Y_AXIS_TITLE, fontsize=FONT_SIZE, color=FONT_COLOR)
plt.gca().yaxis.grid(False)
plt.ylim(ymin=0)

# Output the file
plt.savefig(output_file, **k_plot_fig)
plt.close()
