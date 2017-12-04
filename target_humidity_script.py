#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Target Humidities based on best-practice targets.  Source: Trane
==========================
Outdoor       Indoor
Temp         Humidity
+40            45%
+30            40%
+20            35%
+10            30%
  0            25%
-10            20%
-20            15%

The target humidity should never be above 45% or below 15%.
"""

current_humidity = indigo.devices[281604201].states["sensorValue"]
current_temperature = float(indigo.devices[1899035475].states["temp"])
current_humidity_var = 950128135
target_numidity_var_id = 187913970

# Put the humidity level into a variable to drive the triggers.
# =============================================================
# (You can't currently compare a device state value to a variable value
# directly within a trigger.)

current_humidity = int(current_humidity)
current_humidity = str(current_humidity)
indigo.variable.updateValue(current_humidity_var, current_humidity)

# not more than 45% humidity
if current_temperature >= 40:
    indigo.server.log(u'Updating target humidity level to: 45.')
    indigo.variable.updateValue(target_numidity_var_id, '45')

# not less than 15% humidity
elif current_temperature < -20:
    indigo.server.log(u'Updating target humidity level to: 15.')
    indigo.variable.updateValue(target_numidity_var_id, '15')

# temperature is between -20 and 40
else:
    target_humidity = 45 - ((40 - current_temperature) / 2)
    target_humidity = int(target_humidity)
    target_humidity = str(target_humidity)
    indigo.server.log(u'Updating target humidity level to: {0}.'.format(target_humidity))
    indigo.variable.updateValue(target_numidity_var_id, target_humidity)
