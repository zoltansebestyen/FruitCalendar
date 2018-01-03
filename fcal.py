#!/usr/bin/env python3
"""This little tool aims to generate a printable 'Fruit Calendar'
with the name of a member of the group for each work day"""

import calendar
import xml.etree.ElementTree as etree
import sys

def get_next_name(names, last_name):
    """Generates a cyclic list of names from the list given"""
    if last_name is not None and \
        last_name in names:
        offset = names.index(last_name)
    else:
        offset = 0

    # Should be 31 at most
    for char in range(31):
        yield str(names[(char + offset) % len(names)])

    # FIXME to circumvent iteration errors
    for char in range(100):
        yield "-"

def main():
    """High level module of the code"""
    # TODO nevek should be taken from argv
    nevek = [line.rstrip('\n') for line in open('nevek.txt')]

    last_name_of_last_month = None

    # TODO last_name_of_last_month should be take from argv
    if len(sys.argv) > 1:
        last_name_of_last_month = sys.argv[1]

    fruit_calendar = calendar.HTMLCalendar(calendar.MONDAY)
    next_names = get_next_name(nevek, last_name_of_last_month)

    html_str = fruit_calendar.formatmonth(2018, 1)
    # print(str)

    html_str = html_str.replace("&nbsp;", " ")

    root = etree.fromstring(html_str)
    for elem in root.findall("*//td"):
        # if elem.get("class") != "tue":
        #     continue
        # elem.text += "!"

        br = etree.SubElement(elem, "br")
        br.tail = next(next_names)
        # print(elem.text + str(br.tail))

    print(etree.tostring(root, encoding='utf-8'))

if __name__ == '__main__':
    main()
