#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates a list of Indigo objects that "belong" to plugins.

If a plugin is reported with the name `- plugin not installed -`, look for broken Action items. When you open the
Action, it will be Type: Action Not Found.

TODO: Needs error handling
TODO: built-in function calling plugin device
TODO: Client action calls ppopup controls on plugin device, etc.
"""
import indigo  # noqa
from collections import defaultdict

_plugin_cache = {}
inventory = defaultdict(
    lambda: {
        "control_pages": set(),
        "devices": set(),
        "schedules": set(),
        "triggers": set(),
        "trigger_actions": set(),
    }
)

# skip built-ins for now
skip_list = {
    "Action Collection",
    "Better Email",
    "Email+",
    "INSTEON Commands",
    "Web Server",
    "Z-Wave",
}


# =============================================================================
def get_plugin_name(plugin_id: str) -> str:
    """Get plugin display name with caching."""
    if plugin_id not in _plugin_cache:
        # First time seeing this plugin - look it up and store it. Indigo will
        # handle instances where `plugin_id` refers to a plugin that doesn't
        # exist in the current environment.
        plugin = indigo.server.getPlugin(plugin_id)
        _plugin_cache[plugin_id] = plugin.pluginDisplayName

    return _plugin_cache[plugin_id]


# =============================================================================
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


# =============================================================================
def generate_report():
    """Generate and print the report"""
    separator = "=" * 100

    indigo.server.log(separator)
    indigo.server.log("Plugin Ownership Report")
    indigo.server.log(separator)
    indigo.server.log("Control Pages - Lists each plugin and the control pages that use its actions.")
    indigo.server.log('Devices - Lists each plugin and the devices that "belong" to it.')
    indigo.server.log("Schedules - Lists each plugin and the schedules that use its actions.")
    indigo.server.log("Triggers - Lists each plugin and the triggers that use its actions.")
    indigo.server.log("Trigger Actions - Lists each plugin and the trigger actions that use its actions.")

    # Sort plugins case-insensitively, but filter out skip_list
    sorted_plugins = sorted(
        [(name, data) for name, data in inventory.items() if name not in skip_list],
        key=lambda p: p[0].lower(),
    )

    for plugin_name, categories in sorted_plugins:
        indigo.server.log(separator)
        indigo.server.log(plugin_name)
        indigo.server.log(separator)

        # Process each category
        for category_key in [
            "control_pages",
            "devices",
            "schedules",
            "triggers",
            "trigger_actions",
        ]:
            # Format category name
            category_display = category_key.replace("_", " ").title()
            indigo.server.log(category_display)

            items = categories[category_key]

            if not items:
                indigo.server.log("    None")
            else:
                # Sort items by name, case-insensitively
                sorted_items = sorted(
                    [(object_name(item_id), item_id) for item_id in items],
                    key=lambda item: item[0].lower(),
                )

                for item_name, item_id in sorted_items:
                    indigo.server.log(f"    {item_name}  [{item_id}]")

        indigo.server.log("")


# =============================================================================
def control_pages():
    """List the control pages that reference plugin actions"""
    for cp in indigo.rawServerRequest("GetControlPageList"):
        for action in cp["PageElemList"]:
            for ag in action["ActionGroup"]["ActionSteps"]:
                if "PluginID" in ag:
                    plugin_name = get_plugin_name(ag["PluginID"])
                    inventory[plugin_name]["control_pages"].add(cp["ID"])

            if 'TargetElemID' in action:
                target = int(action['TargetElemID'])
                dev = indigo.devices[target]
                plugin_name = get_plugin_name(dev.pluginId)
                inventory[plugin_name]["control_pages"].add(target)

# =============================================================================
def devices():
    """List the devices of type plugin"""
    for dev in indigo.rawServerRequest("GetDeviceList"):
        if dev.get("PluginUiName", None):
            plugin_name = dev["PluginUiName"]
            inventory[plugin_name]["devices"].add(dev["ID"])


# =============================================================================
def schedules():
    """List the schedules that reference plugin actions"""
    for sched in indigo.rawServerRequest("GetEventScheduleList"):
        for action in sched["ActionGroup"]["ActionSteps"]:
            if action.get("PluginID", None):
                plugin_name = get_plugin_name(action["PluginID"])
                inventory[plugin_name]["schedules"].add(sched["ID"])


# =============================================================================
def triggers():
    """List the triggers of type plugin. Triggers can be associated with
    plugins and also execute plugin actions -- even those of other plugins."""
    for trig in indigo.rawServerRequest("GetEventTriggerList"):
        # Plugin Triggers
        if trig.get("PluginUiName", None):
            plugin_name = trig["PluginUiName"]
            inventory[plugin_name]["triggers"].add(trig["ID"])

        # Trigger plugin actions (from both plugin triggers and built-in triggers)
        if trig.get("ActionGroup", None):
            for action in trig["ActionGroup"]["ActionSteps"]:
                if action.get("PluginID", None):
                    plugin_name = get_plugin_name(action["PluginID"])
                    inventory[plugin_name]["trigger_actions"].add(trig["ID"])


# Assemble the data
control_pages()
devices()
schedules()
triggers()

# Output the results
generate_report()
