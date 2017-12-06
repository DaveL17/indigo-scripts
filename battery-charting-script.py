#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

try:
    import sys
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError, e:
    sys.exit(u"The matplotlib and numpy modules are required to use this script.")

# =================== User Settings ===================
output_file = '/Library/Application Support/Perceptive Automation/Indigo 7/IndigoWebServer/images/controls/static/battery_test.png'  # Indigo 7 installs

chart_title = 'Battery Health'
x_axis_title = ''
y_axis_title = ''

background_color = '#000000'
chart_height = 4.5
chart_width = 6
font_color = '#FFFFFF'
font_name = 'Lato Light'
font_size = 9
grid_color = '#888888'
grid_style = 'dotted'
show_data_labels = True
title_font_size = 9

battery_full_color = '#0000CC'
battery_caution_color = '#FFFF00'
battery_low_color = '#FF0000'
battery_caution_level = 10
battery_low_level = 5

# =================== kwarg Settings ===================
k_bar_fig = {'align': 'center',
             'alpha': 1.0,
             'height': 0.5,
             'zorder': 3
             }

k_grid_fig = {'which': 'major',
              'color': grid_color,
              'linestyle': grid_style,
              'zorder': 0
              }

k_plot_fig = {'bbox_extra_artists': None,
              'bbox_inches': 'tight',
              'dpi': 100,
              'edgecolor': background_color,
              'facecolor': background_color,
              'format': None,
              'frameon': None,
              'orientation': None,
              'pad_inches': 0.1,
              'papertype': None,
              'transparent': True,
              }

k_title_fig = {'fontname': font_name,
               'fontsize': title_font_size,
               'color': font_color,
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

    if device_dict == {}:
        device_dict['No Battery Devices'] = 0

except Exception, e:
    indigo.server.log(u"Error reading battery devices: %s" % e)

# Parse the battery device dictionary for plotting.
try:
    for key, value in sorted(device_dict.iteritems(), reverse=True):
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

        if battery_level <= battery_low_level:
            bar_colors.append(battery_low_color)
        elif battery_low_level < battery_level <= battery_caution_level:
            bar_colors.append(battery_caution_color)
        else:
            bar_colors.append(battery_full_color)

except Exception, e:
    indigo.server.log(u"Error parsing chart data: {0}".format(e))

# Create a range of values to plot on the Y axis, since we can't plot on device names.
y_axis = np.arange(len(y_values))

# Plot the figure
plt.figure(figsize=(chart_width, chart_height))

# Adding 1 to the y_axis pushes the bar to spot 1 instead of spot 0 -- getting it off the axis.
plt.barh((y_axis + 1), x_values, color=bar_colors, **k_bar_fig)

if show_data_labels:
    for ii in range(len(y_axis)):
        plt.annotate("%3d" % x_values[ii], xy=((x_values[ii] - 5), (y_axis[ii]) + 0.88), xycoords='data', textcoords='data', fontsize=font_size, color=font_color)

# Chart
plt.title(chart_title, **k_title_fig)
plt.grid(**k_grid_fig)

# X Axis
plt.xticks(fontsize=font_size, color=font_color)
plt.xlabel(x_axis_title, fontsize=font_size, color=font_color)
plt.gca().xaxis.grid(True)
plt.xlim(xmin=0, xmax=100)

# Y Axis
# The addition of 0.05 to the y_axis better centers the labels on the bars
# (for 2-line labels.) For 1 line labels, change 1.05 to 1.0.
plt.yticks((y_axis + 1.05), y_values, fontsize=font_size, color=font_color)
plt.ylabel(y_axis_title, fontsize=font_size, color=font_color)
plt.gca().yaxis.grid(False)
plt.ylim(ymin=0)

# Output the file
plt.savefig(output_file, **k_plot_fig)
plt.close()
