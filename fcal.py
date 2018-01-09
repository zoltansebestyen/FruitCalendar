#!/usr/bin/env python3
"""This little tool aims to generate a printable 'Fruit Calendar'
with the name of a member of the group for each work day"""

import calendar
import xml.etree.ElementTree as etree
import sys
import locale
import datetime
import click

# Super hack to get full names in HTML calendar
calendar.day_abbr = calendar.day_name

NO_NAME_LABEL = "-"

def get_next_name(names, last_name_used, days_to_skip, month_length=31):
    """Generates a cyclic list of names from the list given
        names: list of names to generate
        last_name_used: last name used last month, we'll skip names until this one
    """
    if last_name_used is not None and last_name_used != '':
        if last_name_used in names:
            name_offset = names.index(last_name_used)
        else:
            raise Exception("No such name %s" % last_name_used)
    else:
        name_offset = 0

    # Skip first day_offset days if needed
    # Generate list of names
    for position in range(month_length):
        if days_to_skip and  str(position) in days_to_skip:
            yield NO_NAME_LABEL
        else:
            yield str(names[(position + name_offset) % len(names)])

    # Fill in the first few days of the next month
    for _ in range(100):
        yield NO_NAME_LABEL

# from https://stackoverflow.com/questions/4130922/
# how-to-increment-datetime-by-custom-months-in-python-without-using-library
def add_months(sourcedate, months):
    """Adds specified number of month to current date"""
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)

@click.command()
@click.option('--last_name_of_last_month', default=None, help='Where from continue the list')
@click.option('--month', default='next', help="Which month to print, can be 'current' or 'next'")
@click.option('--days_to_skip', default=None,
              help="comma separated list of days to skip in the month")
@click.option('--names_file', default='names.txt',
              help="File containing list of names, each one a line")
@click.option('--calendar_title', default='Fruit Calendar')
def print_calendar(last_name_of_last_month, month, days_to_skip, names_file,
                   calendar_title):
    """Prints a HTML calendar to the stdout
    Sample usage:
    python3 fcal.py --month next --last_name_of_last_month 'Ari Marcell'  --days_to_skip 2,5"""
    nevek = [line.rstrip('\n') for line in open(names_file)]

    loc = locale.getlocale() # get current locale

    fruit_calendar = calendar.LocaleHTMLCalendar(calendar.MONDAY, loc)
    next_names = get_next_name(nevek,
                               last_name_of_last_month,
                               days_to_skip.split(",") if days_to_skip else None)

    somedate = datetime.date.today()
    if month == 'current':
        pass
    elif month == 'next':
        somedate = add_months(somedate, 1)
    else:
        raise Exception("Only values 'current and 'next' are accepted")

    html_str = fruit_calendar.formatmonth(somedate.year, somedate.month)

    html_str = html_str.replace("&nbsp;", " ")

    root = etree.fromstring(html_str)

    header = list(list(root)[0])[0]
    (yearstr, monthstr) = header.text.split(" ")

    if loc[0] == 'hu_HU':
        header.text = "%s %s %s" % (calendar_title, monthstr, yearstr)
    else:
        header.text = "%s %s %s" % (calendar_title, yearstr, monthstr)

    root.attrib = {k:v for (k, v) in root.attrib.items() if k == 'class'}

    for elem in root.findall("tr"):
        children = elem.getchildren()
        if len(children) == 1:
            continue

        elem.remove(children[calendar.SUNDAY])
        elem.remove(children[calendar.SATURDAY])

    for elem in root.findall("*//td"):
        if elem.get('class') != 'noday':
            dayno = etree.SubElement(elem, "span")
            dayno.attrib['class'] = 'day'
            dayno.text = elem.text
            elem.text = ''

            name = etree.SubElement(elem, "span")
            name.attrib['class'] = 'name'
            name.text = next(next_names)

    sys.stdout.write(
        """<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" type="text/css" href="fcal.css">
  <meta charset="UTF-8">
<title>""" + calendar_title + """</title>
</head>
<body>
<div class='month'>
<img src='train-fruits-16063547.jpg' width="260" height="94"
     style="margin:0px auto;display:block"/>
 </div>
""")
    sys.stdout.flush()
    sys.stdout.buffer.write(etree.tostring(root, encoding='utf-8'))
    sys.stdout.write(
        """</body>
</html>""")
    sys.stdout.flush()

if __name__ == '__main__':
     # pylint: disable=E1101,E1120
    print_calendar()
