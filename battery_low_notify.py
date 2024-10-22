"""
Simple script to notify of devices with low battery levels.

In order for the script to function, you must replace the numbers `123` with the applicable Indigo variable IDs.
Alternatively, you can simply set `target_level` to any integer between 0 - 100 and email address to a valid email
string.
"""

try:
    import indigo  # noqa
except ImportError:
    ...

target_level = int(indigo.variables[123].value)  # 123 = Indigo variable ID or integer between 0-100
email_address = indigo.variables[123].value  # 123 = Indigo variable ID or email string
email_body = ""

for dev in indigo.devices.iter():
    if dev.batteryLevel:
        if dev.batteryLevel <= target_level:
            email_body += f"{dev.name} battery level: {dev.batteryLevel}\n"

if email_body != "":
    email_body = "The following Indigo devices have low battery levels:\n" + email_body
    indigo.server.sendEmailTo(email_address, subject="Indigo Low Battery Alert", body=email_body)
