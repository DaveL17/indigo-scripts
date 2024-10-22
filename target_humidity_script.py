#!/usr/bin/env python3.11
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

import indigo  # noqa


CURRENT_HUMIDITY       = indigo.devices[281604201].states["sensorValue"]
CURRENT_TEMPERATURE    = float(indigo.devices[1899035475].states["temp"])
CURRENT_HUMIDITY_VAR   = 950128135
TARGET_HUMIDITY_VAR_ID = 187913970

# Put the humidity level into a variable to drive the triggers.
# =============================================================
# You can't currently compare a device state value to a variable value directly within a trigger.

CURRENT_HUMIDITY = round(CURRENT_HUMIDITY)
CURRENT_HUMIDITY = str(CURRENT_HUMIDITY)
indigo.variable.updateValue(CURRENT_HUMIDITY_VAR, CURRENT_HUMIDITY)

# Upper bound - not more than 45% humidity
if CURRENT_TEMPERATURE >= 40:
    indigo.server.log("Updating target humidity level to: 45.")
    indigo.variable.updateValue(TARGET_HUMIDITY_VAR_ID, '45')

# Lower bound - not less than 15% humidity
elif CURRENT_TEMPERATURE < -20:
    indigo.server.log("Updating target humidity level to: 15.")
    indigo.variable.updateValue(TARGET_HUMIDITY_VAR_ID, '15')

# Temperature is between -20 and 40
else:
    target_humidity = 45 - ((40 - CURRENT_TEMPERATURE) / 2)
    target_humidity = round(target_humidity)
    indigo.server.log(f'Updating target humidity level to: {target_humidity}.')
    indigo.variable.updateValue(TARGET_HUMIDITY_VAR_ID, target_humidity)
