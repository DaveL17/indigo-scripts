#! /usr/bin/env python3.11
# -*- coding: utf-8 -*-

"""
A script that demonstrates yet another way to add information to the Apple Calendar.

This example uses the Indigo reflector and its public facing web assets folder to share data, so (as shown) it will
break when you upgrade Indigo to a new version. For a more permanent solution, save the resulting iCalendar file to a
web server location that doesn't change when Indigo is updated like a Raspberry Pi or Django Server. Using Apple
Shortcuts to add information to calendars is still probably the most straightforward method to add data to your
calendar, but it's not always the best option for certain situations. For example, you might want to put weather
forecast information on your calendar that will automatically refresh as new data come in and drop information that
becomes dated. In this case, a calendar subscription may be best.

Instructions:
- Modify the below script to suit your needs. The events below are placeholders.
- Run the script and make sure to save the ICS file to a location that is a web server. You can run it from an Indigo
  schedule, trigger or outside Indigo.
- Subscribe to the resulting ICS file in Calendar.app. In Calendar:
  1. Go to File -> New Calendar Subscription
  2. Enter the full reflector address that points to the ICS file, i.e.,
     'https://MY_REFLECTOR_NAME.indigodomo.net/public/my_ics_file.ics'. Note this example uses the public folder, so
     authentication isn't needed (and anyone with the precise url will be able to view it.)
  3. Set the subscription settings as desired. Note that 'Location' controls whether the subscription is shared with
     all your devices (iCloud) or locally.
  4. Note that the shortest subscription refresh time is 5 minutes (this is controlled by Calendar.app.)

There is a ton of potential complexity -- especially with times and timezones -- so be sure to test your script
extensively before relying on it. This is not even remotely close to all the possible properties and, in a way, is
(close to) the minimum number of property elements. This example doesn't take into account things like timezones or
alternative (non-Gregorian) calendars. Sample output is shown below.

See also:
Internet Calendaring and Scheduling Core Object Specification (iCalendar) https://www.rfc-editor.org/rfc/rfc5545.html
iCalendar.org https://icalendar.org
iCalendar Python Library https://icalendar.readthedocs.io/en/latest/ (not used in this example)
Subscribe to Calendars https://support.apple.com/guide/calenda ... cl1022/mac
"""


from datetime import datetime

# A valid web server location and a data source object
ICS_FILE_LOC = f"{indigo.server.getInstallFolderPath()}/Web Assets/public/davecal.ics"
WEATHER_DEV  = indigo.devices[1655952153]

# Calendar-wide properties
payload = f"""
BEGIN:VCALENDAR
CALSCALE:GREGORIAN
VERSION:2.0

"""

# Individual events
for nnn in range(0, 5):
    date     = WEATHER_DEV.states[f'daily_{nnn}_dt']  # timestamp
    date_fmt = datetime.fromtimestamp(date).strftime('%Y%m%d')  # "20240827"
    low      = WEATHER_DEV.states[f'daily_{nnn}_temp_min']  # float
    high     = WEATHER_DEV.states[f'daily_{nnn}_temp_max']  # float
    summary  = WEATHER_DEV.states[f'daily_{nnn}_summary']  # string

    payload += f"""BEGIN:VEVENT
DTSTART;VALUE=DATE:{date_fmt}
SUMMARY:{low:0.0f}º / {high:0.0f}º
DESCRIPTION:{summary}
END:VEVENT

"""

# End of calendar
payload += "END:VCALENDAR"

# Write ICS file to server location
with open(ICS_FILE_LOC, "w", encoding='utf-8') as outfile:
    outfile.write(payload)

# indigo.server.log(payload)

# Sample output format
"""
BEGIN:VCALENDAR
CALSCALE:GREGORIAN
VERSION:2.0

BEGIN:VEVENT
DTSTART;VALUE=DATE:20240827
SUMMARY:74º / 101º
DESCRIPTION:Expect a day of partly cloudy with rain
END:VEVENT

[snip]

END:VCALENDAR
"""
