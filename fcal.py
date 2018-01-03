#!/usr/bin/env python3
"""This little tool aims to generate a printable 'Fruit Calendar'
with the name of a member of the group for each work day"""

import calendar
import xml.etree.ElementTree as etree
import sys
import locale


NO_NAME_LABEL="-"

def get_next_name(names, last_name_used, day_offset=0, month_length=31):
    """Generates a cyclic list of names from the list given
        names: list of names to generate
        last_name_used: last name used last month, we'll skip names until this one
    """
    if last_name_used is not None:
        if last_name_used in names:
            name_offset = names.index(last_name_used)
        else:
            raise Exception("No such name %s" % last_name_used)
    else:
        name_offset = 0

    # Skip first day_offset days if needed
    for _ in range(day_offset):
        yield NO_NAME_LABEL

    # Generate list of names
    for position in range(month_length - day_offset):
        yield str(names[(position + name_offset) % len(names)])

    # Fill in the first few days of the next month
    for _ in range(100):
        yield NO_NAME_LABEL

def main():
    """High level module of the code"""
    # TODO nevek should be taken from argv
    nevek = [line.rstrip('\n') for line in open('nevek.txt')]

    last_name_of_last_month = None

    # TODO last_name_of_last_month should be take from argv
    if len(sys.argv) > 1:
        last_name_of_last_month = sys.argv[1]

    loc = locale.getlocale() # get current locale
    fruit_calendar = calendar.LocaleHTMLCalendar(calendar.MONDAY, loc)
    next_names = get_next_name(nevek, last_name_of_last_month)

    html_str = fruit_calendar.formatmonth(2018, 1)
    # print(str)

    html_str = html_str.replace("&nbsp;", " ")

    root = etree.fromstring(html_str)
    for elem in root.findall("*//td"):

        br = etree.SubElement(elem, "br")
        br.tail = next(next_names)

    sys.stdout.write(
"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
<title>Page Title</title>
</head>
<body>""")
    sys.stdout.flush()
    sys.stdout.buffer.write(etree.tostring(root, encoding='utf-8'))
    sys.stdout.write(
"""</body>
</html>""")
    sys.stdout.flush()

if __name__ == '__main__':
    main()
