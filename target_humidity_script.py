#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
Target Humidities based on best-practice targets.  Source: Trane
==========================
Outdoor         Indoor
Temp         Humidity
+40            45%
+30            40%
+20            35%
+10            30%
0               25%
-10            20%
-20            15%
"""

# Put the humidity level into a variable to drive the triggers. (You can't currently compare a device value to a variable value directly within a trigger.)
currentHumidity = indigo.devices[281604201].states["sensorValue"]
currentHumidity = int(currentHumidity)
currentHumidity = str(currentHumidity)
indigo.variable.updateValue(950128135, currentHumidity)

# Get the current outdoor temperature.
currentTemp = float(indigo.devices[1899035475].states["temp"])

# not more than 45% humidity
if currentTemp >= 40:
    indigo.server.log(u'Updating target humidity level to: 45.')
    indigo.variable.updateValue(187913970, '45')

# not less than 15% humidity
elif currentTemp < -20:
    indigo.server.log(u'Updating target humidity level to: 15.')
    indigo.variable.updateValue(187913970, '15')

# temperature is between -20 and 40
else:
    targetHumidity = 45 - ((40 - currentTemp) / 2)
    targetHumidity = int(targetHumidity)
    targetHumidity = str(targetHumidity)
    indigo.server.log(u'Updating target humidity level to: %s.' % targetHumidity)
    indigo.variable.updateValue(187913970, targetHumidity)
