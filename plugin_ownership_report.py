#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates a list of Indigo objects that "belong" to plugins.

If a plugin is reported with the name `- plugin not installed -`, look for broken Action items. When you open the
Action, it will be: Type: Action Not Found.
"""
import indigo  # noqa

inventory = {'devices': {}, 'triggers': {}, 'trigger_actions': {}, 'control_pages': {}}

def object_name(obj_id: str) -> str:
    """Get the object's name."""
    try:
        my_id = int(obj_id)
        for collection in (indigo.devices, indigo.triggers, indigo.controlPages):
            if my_id in collection:
                return collection[my_id].name
        return "?"
    except ValueError:
        return obj_id

def generate_report():
    """ Generate and print the report """
    seperator = '=' * 100
    indigo.server.log(seperator)
    indigo.server.log("Plugin Ownership Report")
    indigo.server.log(seperator)
    indigo.server.log('Devices - Lists each plugin and the devices that "belong" to it.')
    indigo.server.log('Triggers - Lists each plugin and the triggers that "belong" to it.')
    indigo.server.log('Trigger Actions - Lists each plugin and the triggers that call one of its actions.')
    indigo.server.log('Control Pages - Lists each plugin and the control pages that call one of its actions.')

    for category, plugins in inventory.items():
        indigo.server.log(seperator)
        category = category.replace("_", " ").title()
        indigo.server.log(f"{category}")
        indigo.server.log(seperator)
        for plug, items in plugins.items():
            indigo.server.log(plug)
            for item in items:
                name = object_name(item)
                indigo.server.log(f"\t{name}  [{item}]")
        indigo.server.log("")

# Devices
# =============================================================================
# List the devices of type plugin
for dev in indigo.rawServerRequest("GetDeviceList"):
    if dev.get('PluginUiName', None):
        plugin_name = dev['PluginUiName']
        if plugin_name not in inventory['devices']:
            inventory['devices'][plugin_name] = []
        inventory['devices'][plugin_name].append(dev['ID'])

# Triggers
# =============================================================================
# List the triggers of type plugin. Triggers can be associated with plugins and
# also execute plugin actions -- even those of other plugins.
for trig in indigo.rawServerRequest("GetEventTriggerList"):
    if trig.get('PluginUiName', None):
        plugin_name = trig['PluginUiName']
        if plugin_name not in inventory['triggers']:
            inventory['triggers'][plugin_name] = []
        inventory['triggers'][plugin_name].append(trig['ID'])

        # Trigger plugin actions
        # =====================================================================
        for action in trig['ActionGroup']['ActionSteps']:
            if action.get('PluginID', None):
                plugin = indigo.server.getPlugin(action['PluginID'])
                plugin_name = plugin.pluginDisplayName
                if plugin_name not in inventory['trigger_actions']:
                    inventory['trigger_actions'][plugin_name] = []
                inventory['trigger_actions'][plugin_name].append(trig['ID'])

# Control Pages
# =============================================================================
# List the control pages that reference plugin actions
for cp in indigo.rawServerRequest("GetControlPageList"):
    for action in cp['PageElemList']:
        for ag in action['ActionGroup']['ActionSteps']:
            if 'PluginID' in ag:
                plugin = indigo.server.getPlugin(ag['PluginID'])
                plugin_name = plugin.pluginDisplayName
                if plugin_name not in inventory['control_pages']:
                    inventory['control_pages'][plugin_name] = []
                inventory['control_pages'][plugin_name].append(cp['ID'])

generate_report()
