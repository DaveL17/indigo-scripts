#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates a list of Indigo objects that "belong" to plugins.

If a plugin is reported with the name `- plugin not installed -`, look for broken Action items. When you open the
Action, it will be: Type: Action Not Found.
"""
import indigo  # noqa
from collections import defaultdict

inventory = {
    'control_pages': defaultdict(set),  # Use sets to auto-deduplicate
    'devices': defaultdict(set),
    'schedules': defaultdict(set),
    'triggers': defaultdict(set),
    'trigger_actions': defaultdict(set)
}


# skip built-ins for now
skip_list = {
    "Action Collection",
    "Better Email",
    "Email+",
    "INSTEON Commands",
    "Web Server",
    "Z-Wave",
}


def generate_report():
    """ Generate and print the report """
    def object_name(obj_id: str) -> str:
        """Get the object's name."""
        try:
            my_id = int(obj_id)
            for collection in (
                indigo.devices,
                indigo.triggers,
                indigo.controlPages,
                indigo.schedules,
            ):
                if my_id in collection:
                    return collection[my_id].name
            return "?"
        except ValueError:
            return obj_id

    separator = '=' * 100
    indigo.server.log(separator)
    indigo.server.log("Plugin Ownership Report")
    indigo.server.log(separator)
    indigo.server.log('Control Pages - Lists each plugin and the control pages that use its actions.')
    indigo.server.log('Devices - Lists each plugin and the devices that "belong" to it.')
    indigo.server.log('Schedules - Lists each plugin and the schedules that use its actions.')
    indigo.server.log('Triggers - Lists each plugin and the triggers that use its actions.')
    indigo.server.log('Trigger Actions - Lists each plugin and the triggers actions that use its actions.')

    for category, plugins in inventory.items():

        # Skip empty categories
        if not any(plugin not in skip_list for plugin in plugins):
            continue

        indigo.server.log(separator)
        category = category.replace("_", " ").title()
        indigo.server.log(f"{category}")
        indigo.server.log(separator)
        for plug, items in sorted(plugins.items(), key=lambda p: p[0].lower()):  # sort by plugin name
            sorted_items = sorted([(object_name(a), a) for a in items], key=lambda item: item[0].lower())  # Sort by object name
            if plug not in skip_list:
                indigo.server.log(plug)
                for item in sorted_items:  # item is an Indigo ID number.
                    indigo.server.log(f"    {item[0]}  [{item[1]}]")
        indigo.server.log("")


# Control Pages
# =============================================================================
# List the control pages that reference plugin actions
def control_pages():
    for cp in indigo.rawServerRequest("GetControlPageList"):
        for action in cp['PageElemList']:
            for ag in action['ActionGroup']['ActionSteps']:
                if 'PluginID' in ag:
                    plugin = indigo.server.getPlugin(ag['PluginID'])
                    plugin_name = plugin.pluginDisplayName
                    inventory['control_pages'][plugin_name].add(cp['ID'])


# Devices
# =============================================================================
# List the devices of type plugin
def devices():
    for dev in indigo.rawServerRequest("GetDeviceList"):
        if dev.get('PluginUiName', None):
            plugin_name = dev['PluginUiName']
            inventory['devices'][plugin_name].add(dev['ID'])


# Schedules
# =============================================================================
def schedules():
    for sched in indigo.rawServerRequest("GetEventScheduleList"):
        for action in sched['ActionGroup']['ActionSteps']:
            if action.get('PluginID', None):
                plugin = indigo.server.getPlugin(action["PluginID"])
                plugin_name = plugin.pluginDisplayName
                inventory['schedules'][plugin_name].add(sched['ID'])


# Triggers
# =============================================================================
# List the triggers of type plugin. Triggers can be associated with plugins and
# also execute plugin actions -- even those of other plugins.
def triggers():
    for trig in indigo.rawServerRequest("GetEventTriggerList"):
        # Plugin Triggers
        if trig.get('PluginUiName', None):
            plugin_name = trig['PluginUiName']
            inventory['triggers'][plugin_name].add(trig['ID'])

            # Trigger plugin actions
            # =====================================================================
            for action in trig['ActionGroup']['ActionSteps']:
                if action.get('PluginID', None):
                    plugin = indigo.server.getPlugin(action['PluginID'])
                    plugin_name = plugin.pluginDisplayName
                    inventory['trigger_actions'][plugin_name].add(trig['ID'])

        # Built-in Triggers that call a plugin Actions
        elif trig.get("ActionGroup", None):
            for action in trig["ActionGroup"]["ActionSteps"]:
                if action.get("PluginID", None):
                    plugin = indigo.server.getPlugin(action["PluginID"])
                    plugin_name = plugin.pluginDisplayName
                    inventory["trigger_actions"][plugin_name].add(trig["ID"])


# Assemble the data
control_pages()
devices()
schedules()
triggers()

# Output the results
generate_report()
