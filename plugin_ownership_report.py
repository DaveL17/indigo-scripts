#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates a list of Indigo objects that "belong" to plugins.

If a plugin is reported with the name `- plugin not installed -`, look for broken Action items. When you open the
Action, it will be Type: Action Not Found.
TODO: Needs robust error handling
TODO: Needs unit testing
"""
import indigo  # noqa
from collections import defaultdict

__version__ = "0.1.3"
_plugin_cache = {}

# Initialize an inventory dictionary with default empty collections.
# It uses sets so only one instance of a value is ever tracked.
inventory = defaultdict(
    lambda: {
        "action_groups": set(),
        "control_pages": set(),
        "devices": set(),
        "schedules": set(),
        "triggers": set(),
        "trigger_actions": set(),
    }
)

# skip built-ins
skip_list = {
    "com.perceptiveautomation.indigoplugin.ActionCollection",  # Action Collection
    "com.perceptiveautomation.indigoplugin.devicecollection",  # virtual devices
    "com.flyingdiver.indigoplugin.betteremail",  # Better Email
    "com.indigodomo.email",  # Email+
    "com.perceptiveautomation.indigoplugin.InsteonCommands",  # Insteon
    "com.indigodomo.webserver",  # Web Server
    "com.perceptiveautomation.indigoplugin.zwave",  # Z-wave
    "",  # if a pluginId is empty, we don't care about it (i.e., X-10)
    None
}


# =============================================================================
def generate_report():
    """Generate and print the report"""
    separator = "=" * 100
    indigo.server.log(separator)
    indigo.server.log(f"Plugin Ownership Report v{__version__}")
    indigo.server.log(separator)
    indigo.server.log("Control Pages - Lists each plugin and the control pages that use its actions.")
    indigo.server.log('Devices - Lists each plugin and the devices that "belong" to it.')
    indigo.server.log("Schedules - Lists each plugin and the schedules that use its actions.")
    indigo.server.log("Triggers - Lists each plugin and the triggers that use its actions.")
    indigo.server.log("Trigger Actions - Lists each plugin and the trigger actions that use its actions.")

    # Sort plugins case-insensitively, but filter out skip_list
    sorted_plugins = sorted([(get_plugin_name(name), data) for name, data in inventory.items()], key=lambda p: p[0].lower(),)

    if len(sorted_plugins) == 0:
        indigo.server.log("")
        indigo.server.log(f"=== No plugin owned objects found. ===")

    for plugin_name, categories in sorted_plugins:
        indigo.server.log(separator)
        indigo.server.log(plugin_name)
        indigo.server.log(separator)

        # Process each category
        for category_key in [
            "action_groups",
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
                    [(get_object_name(item_id), item_id) for item_id in items],
                    key=lambda item: item[0].lower(),
                )

                for item_name, item_id in sorted_items:
                    indigo.server.log(f"    {item_name}  [{item_id}]")

        indigo.server.log("")

    indigo.server.log(f"=== End of Report ===")


# =============================================================================
def get_object_name(obj_id: str) -> str:
    """Get the object's name."""
    try:
        my_id = int(obj_id)
        for collection in (
            indigo.actionGroups,
            indigo.controlPages,
            indigo.devices,
            indigo.schedules,
            indigo.triggers,
        ):
            if my_id in collection:
                return collection[my_id].name
        return "Name unavailable"
    except ValueError:
        return obj_id


# =============================================================================
def get_plugin_name(plugin_id: str) -> str:
    """Get plugin display name with caching."""
    if plugin_id not in _plugin_cache:
        # First time seeing this plugin - look it up and store it. Indigo will
        # handle instances where `plugin_id` refers to a plugin that doesn't
        # exist in the current environment.
        try:
            plugin = indigo.server.getPlugin(plugin_id)
            plugin_name = plugin.pluginDisplayName
        except TypeError:
            # this is meant to apply to things that don't have a plugin_id if
            # we haven't already skipped them.
            plugin_name = "- plugin not installed -"
        if plugin_name == "- plugin not installed -":
            plugin_name = f"Plugin not Installed: [{plugin_id}]"
        _plugin_cache[plugin_id] = plugin_name

    return _plugin_cache[plugin_id]


def action_groups():
    """List plugin actions added to action groups."""
    for action_group in indigo.rawServerRequest("GetActionGroupList"):
        for action in action_group['ActionSteps']:
            if action.get('PluginID', None) not in skip_list:
                indigo.server.log(f"{action['PluginID']}")
                inventory[action["PluginID"]]["action_groups"].add(action_group["ID"])


# =============================================================================
def control_pages():
    """List the control pages that reference plugin actions"""
    for control_page in indigo.rawServerRequest("GetControlPageList"):
        # Users do not need to see the internal page references.
        if control_page['Name'] == "_internal_devices_":
            continue
        for action in control_page["PageElemList"]:
            for ag in action["ActionGroup"]["ActionSteps"]:
                if ag.get("PluginID", None) not in skip_list:
                    inventory[ag["PluginID"]]["control_pages"].add(control_page["ID"])

            # Get plugin devices that are referenced by built-in controls. For
            # example, Client Action  -> Popup Controls
            obj = None
            if action.get('TargetElemID', None):
                elem_id = action["TargetElemID"]
                # TargetElemID is a device
                if elem_id in indigo.devices:
                    obj = indigo.devices[elem_id]
                # TargetElemID is a trigger
                elif elem_id in indigo.triggers:
                    obj = indigo.triggers[elem_id]
                # TargetElemID is something else
                else:
                    indigo.server.log(f"{elem_id} is not a device or trigger")

                if hasattr(obj, 'pluginId'):
                    if obj.pluginId not in skip_list:
                        inventory[obj.pluginId]["control_pages"].add(obj.id)


# =============================================================================
def devices():
    """List the devices of type plugin"""
    for dev in indigo.rawServerRequest("GetDeviceList"):
        if dev.get("PluginID", None) not in skip_list:
            inventory[dev["PluginID"]]["devices"].add(dev["ID"])


# =============================================================================
def schedules():
    """List the schedules that reference plugin actions"""
    for sched in indigo.rawServerRequest("GetEventScheduleList"):
        for action in sched["ActionGroup"]["ActionSteps"]:
            if action.get("PluginID", None) not in skip_list:
                inventory[action["PluginID"]]["schedules"].add(sched["ID"])


# =============================================================================
def triggers():
    """List the triggers of type plugin. Triggers can be associated with
    plugins and also execute plugin actions -- even those of other plugins."""
    for trig in indigo.rawServerRequest("GetEventTriggerList"):
        # Plugin Triggers
        if trig.get("PluginID", None) not in skip_list:
            inventory[trig["PluginID"]]["triggers"].add(trig["ID"])

        # Trigger actions (from both plugin triggers and built-in triggers)
        if trig.get("ActionGroup", None):
            for action in trig["ActionGroup"]["ActionSteps"]:
                if action.get("PluginID", None) not in skip_list:
                    inventory[action["PluginID"]]["trigger_actions"].add(trig["ID"])


# Assemble the data
action_groups()
control_pages()
devices()
schedules()
triggers()

# Output the results
generate_report()
