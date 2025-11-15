#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates a list of Indigo objects that "belong" to plugins.

If a plugin is reported with the name `- plugin not installed -`, look for broken Action items. When you open the
Action, it will be Type: Action Not Found.
TODO: Needs robust error handling
TODO: Needs unit testing
"""
from collections import defaultdict
from datetime import datetime
import indigo  # noqa
import sys

__version__ = "0.1.19"
_plugin_cache = {}
_print_to_event_log = True
_print_to_file = False
_path_to_print = indigo.server.getInstallFolderPath() + "/logs/"

# Initialize an inventory dictionary with default empty collections. It uses lists so there can be multiple entries for
# a single entry. For example, a control page may reference the same plugin device multiple times for different states.
inventory = defaultdict(
    lambda: {
        "action_groups": [],
        "control_pages": [],
        "devices": [],
        "schedules": [],
        "triggers": [],
        "trigger_actions": [],
    }
)

# Used to populate inventory key lookups.
CATEGORIES = [
    "action_groups",
    "control_pages",
    "devices",
    "schedules",
    "triggers",
    "trigger_actions",
]

# Used to look up object IDs to determine object types
OBJ_TYPES = (
    indigo.actionGroups,
    indigo.controlPages,
    indigo.devices,
    indigo.schedules,
    indigo.triggers,
)

# List of installed plugins (both enabled and disabled)
plugin_list = indigo.server.getPluginList(includeDisabled=True)

# Skip certain plugin id's for things like built-ins or empty plugin id fields.
SKIP_LIST = {
    "com.flyingdiver.indigoplugin.betteremail",  # Better Email
    "com.indigodomo.email",  # Email+
    "com.indigodomo.webserver",  # Web Server
    "com.perceptiveautomation.indigoplugin.ActionCollection",  # Action Collection
    "com.perceptiveautomation.indigoplugin.devicecollection",  # virtual devices
    "com.perceptiveautomation.indigoplugin.InsteonCommands",  # Insteon
    "com.perceptiveautomation.indigoplugin.zwave",  # Z-wave
    "",  # if a pluginId is empty (i.e., X-10), we don't care about it.
    None
}

# Validate output toggles
# =============================================================================
if not _print_to_event_log and not _print_to_file:
    indigo.server.log(f"You must direct the report's output to either the log or to a file.", isError=True)
    sys.exit(1)


# =============================================================================
def add_to_inventory(plugin_id: str, category: str, details: dict):
    """Add entries to inventory dict"""
    inventory[plugin_id][category].append(details)


# =============================================================================
def generate_report():
    """Generate and print the report"""
    separator = "=" * 100
    report = f"Plugin Reference Report v{__version__}"

    # Sort plugins case-insensitively
    sorted_plugins = sorted(
        [(name, get_plugin_name(name), data) for name, data in inventory.items()], key=lambda p: p[1].lower()
    )

    # The inventory is empty
    if len(sorted_plugins) == 0:
        report += f"\nNo plugins installed."

    for name, plugin_name, categories in sorted_plugins:
        report += f"\n{separator}\n{plugin_name} [{name}]\n{separator}"

        # Process each category
        for category_key in CATEGORIES:
            # Format category name
            category_display = category_key.replace("_", " ").title()
            items = categories[category_key]
            report += f"\n{category_display}"

            # No entries in the category
            if not items:
                report += "\n    None"
            else:
                # Sort items by name, case-insensitively
                sorted_items = sorted(
                    [(get_object_name(item_id), item_id) for item_id in items], key=lambda item: item[0].lower()
                )

                for item_name, item_id in sorted_items:
                    if 'description' in item_id:
                        report += f"\n    {item_name} | {item_id['id']} | {item_id['description']}"
                    else:
                        report += f"\n    {item_name} | {item_id['id']}"

        report += "\n"

    report += "\n=== End of Report ==="

    if _print_to_event_log:
        indigo.server.log(report)

    if _print_to_file:
        with open(f"{_path_to_print}plugin_reference_report_{datetime.now():%Y-%m-%d_%H-%M-%S}.txt", "w") as file:
            file.write(report)
        indigo.server.log("Report generated")

# =============================================================================
def get_object_name(obj):
    """
    Get the object's name.

    There is a small but possible chance that an ID may be used by more than one object type. In this case, the script
    is going to go with the first object/ID match. If no match is found, "Name unavailable" will be returned.

    TODO: could check all object types and report all matches (if there's more than one).
    """
    obj_id = obj['id']
    try:
        for collection in OBJ_TYPES:
            if obj_id in collection:
                return collection[obj_id].name
    except (KeyError, ValueError):
        pass

    return "Name unavailable"


# =============================================================================
def get_plugin_name(plugin_id: str) -> str:
    """Get plugin display name with caching."""
    if plugin_id not in _plugin_cache:
        # First time seeing this plugin - look it up and store it. Indigo will handle instances where `plugin_id`
        # refers to a plugin that doesn't exist in the current environment.
        try:
            plugin = indigo.server.getPlugin(plugin_id)
            plugin_name = plugin.pluginDisplayName
        except TypeError:
            # This is meant to apply to things that don't have a plugin_id if we haven't already skipped them.
            plugin_name = "- plugin not installed -"

        # This looks duplicative of the next `if`, but it's not. Indigo can also return this plugin name string.
        if plugin_name == "- plugin not installed -":
            plugin_name = f"Plugin not Installed"
        _plugin_cache[plugin_id] = plugin_name

    return _plugin_cache[plugin_id]


# =============================================================================
def action_groups():
    """List action groups that reference plugin objects."""
    for action_group in indigo.rawServerRequest("GetActionGroupList"):
        for action in action_group['ActionSteps']:
            if action.get('PluginID', None) not in SKIP_LIST:
                add_to_inventory(action["PluginID"], "action_groups", {'id': action_group["ID"]})

            # Search for embedded scripts with plugin references (saved as actions). Will match one or more plugin
            # references in the target script.
            elif (action.get("Class", None) == 101) and (action.get("ScriptType", None) == 0):

                for plugin in plugin_list:
                    plugin_id = plugin.pluginId  # Single attribute lookup
                    if plugin_id in action["ScriptSource"] and plugin_id not in SKIP_LIST:
                        add_to_inventory(plugin.pluginId, "action_groups", {
                            'id': action_group["ID"], "description": f"embedded script"})


# =============================================================================
def control_pages():
    """List the control pages that reference plugin objects"""
    for control_page in indigo.rawServerRequest("GetControlPageList"):
        # Users do not need to see the internal page references.
        if control_page['Name'] == "_internal_devices_":
            continue

        for action in control_page["PageElemList"]:
            for ag in action["ActionGroup"]["ActionSteps"]:
                if ag.get("PluginID", None) not in SKIP_LIST:
                    add_to_inventory(ag["PluginID"], "control_pages", {
                        'id': control_page["ID"], 'description': f"built-in control Z-{action['ServerIndex']}"})

                # Search for embedded scripts with plugin references (saved as control page actions). Will match one or
                # more plugin references in the target script.
                elif (ag.get("Class", None) == 101) and (ag.get("ScriptType", None) == 0):

                    for plugin in plugin_list:
                        plugin_id = plugin.pluginId  # Single attribute lookup
                        if plugin_id in ag["ScriptSource"] and plugin_id not in SKIP_LIST:
                            add_to_inventory(plugin_id, "control_pages", {
                                "id": control_page["ID"], "description": f"embedded script control Z-{action['ServerIndex']}"})

            # Get plugin devices and triggers that are referenced by built-in controls. For example,
            # Client Action -> Popup Controls. These don't have a `ServerIndex` because they aren't "on the page".
            obj = None
            if action.get('TargetElemID', None):
                elem_id = action["TargetElemID"]
                # TargetElemID is a device
                if elem_id in indigo.devices:
                    obj = indigo.devices[elem_id]
                # TargetElemID is an action group
                elif elem_id in indigo.actionGroups:
                    obj = indigo.actionGroups[elem_id]
                # TargetElemID is a trigger
                # FIXME: I'm not sure this is a necessary test -- can you fire a trigger from a CP? From an embedded
                #        script perhaps?
                elif elem_id in indigo.triggers:
                    obj = indigo.triggers[elem_id]
                # TargetElemID is something else
                else:
                    pass

                # Check to see if the discovered object has a pluginId attribute. If it does, add the object id to the
                # inventory.
                if hasattr(obj, 'pluginId'):
                    if obj.pluginId not in SKIP_LIST:
                        add_to_inventory(obj.pluginId, "control_pages", {
                            'id': control_page["ID"], 'description': f"Control Z-{action['ServerIndex']}"})


# =============================================================================
def devices():
    """List the devices of type plugin"""
    for dev in indigo.rawServerRequest("GetDeviceList"):
        if dev.get("PluginID", None) not in SKIP_LIST:
            add_to_inventory(dev["PluginID"], "devices", {'id': dev["ID"]})


# =============================================================================
def schedules():
    """List the schedules that reference plugin objects"""
    for sched in indigo.rawServerRequest("GetEventScheduleList"):
        for action in sched["ActionGroup"]["ActionSteps"]:
            if action.get("PluginID", None) not in SKIP_LIST:
                add_to_inventory(action["PluginID"], "schedules", {'id': sched["ID"]})

        # Inspect trigger conditions for plugin references
        if sched['Condition'].get("ScriptType", None) == 0 and sched['Condition'].get("ScriptSource", None):

            for plugin in plugin_list:
                plugin_id = plugin.pluginId
                if plugin_id in sched["Condition"]["ScriptSource"] and plugin_id not in SKIP_LIST:
                    add_to_inventory(plugin.pluginId, "schedules",
                                     {"id": sched["ID"], "description": f"schedule condition"})


# =============================================================================
def triggers():
    """
    List the triggers of type plugin. Triggers can be associated with plugins and also execute plugin actions -- even
    those of other plugins.
    """
    for trig in indigo.rawServerRequest("GetEventTriggerList"):
        # Plugin Triggers
        if trig.get("PluginID", None) not in SKIP_LIST:
            add_to_inventory(trig["PluginID"], "triggers", {'id': trig["ID"]})

        # Trigger actions (from both plugin triggers and built-in triggers)
        if trig.get("ActionGroup", None):
            for action in trig["ActionGroup"]["ActionSteps"]:
                if action.get("PluginID", None) not in SKIP_LIST:
                    add_to_inventory(action["PluginID"], "trigger_actions", {'id': trig["ID"]})

                # Search for embedded scripts with plugin references (saved as actions). Will match one or more plugin
                # references in the target script.
                elif (action.get("Class", None) == 101) and (action.get("ScriptType", None) == 0):

                    for plugin in plugin_list:
                        plugin_id = plugin.pluginId
                        if plugin_id in action["ScriptSource"] and plugin_id not in SKIP_LIST:
                            add_to_inventory(plugin.pluginId, "trigger_actions", {
                                'id': trig["ID"], "description": f"embedded script"})

        # Inspect trigger conditions for plugin references
        if trig['Condition'].get("ScriptType", None) == 0 and trig['Condition'].get("ScriptSource", None):
            for plugin in plugin_list:
                plugin_id = plugin.pluginId
                if plugin_id in trig["Condition"]["ScriptSource"] and plugin_id not in SKIP_LIST:
                    add_to_inventory(plugin.pluginId, "triggers",
                                     {"id": trig["ID"], "description": f"trigger condition"})


# Assemble the data
action_groups()
control_pages()
devices()
schedules()
triggers()

# Output the results
generate_report()
