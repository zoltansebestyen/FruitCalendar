#!/usr/bin/env python3
"""This little tool aims to generate a printable 'Fruit Calendar'
with the name of a member of the group for each work day"""

import calendar
import xml.etree.ElementTree as etree
import sys
import locale
import datetime
import click
import os

import jinja2

import yaml

# Super hack to get full names in HTML calendar
calendar.day_abbr = calendar.day_name

NO_NAME_LABEL = "-"

def get_next_name(names, last_name_used, month_length=31):
    """Generates a cyclic list of names from the list given
        names: list of names to generate
        last_name_used: last name used last month, we'll skip names until this one
    """
    if last_name_used is not None and last_name_used != '':
        if last_name_used in names:
            name_offset = (names.index(last_name_used) + 1) % len(names)
        else:
            raise Exception("No such name %s" % last_name_used)
    else:
        name_offset = 0

    # Generate list of names
    for position in range(month_length):
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

TODAY = datetime.date.today()
THIS_YEAR = TODAY.year
THIS_MONTH = TODAY.month

def parse_days(days_list, month=THIS_MONTH):

    return {
        datetime.datetime(int(d[0]), int(d[1]), int(d[2])) if len(d) == 3
        else
        datetime.datetime(THIS_YEAR, int(d[0]), int(d[1])) if len(d) == 2
        else
        datetime.datetime(THIS_YEAR, month, int(d[0])) # if len(d) == 1
        for d in
        [dstr.split('.') for dstr in days_list]
        }

def parse_config(config_file):
    '''parses config, consisting of days'''
    with open(config_file, 'r') as s:
        config = yaml.load(s)

    retval = (parse_days(config['holidays']), parse_days(config['working_days']))
    return retval


@click.command()
@click.option('--last_name_of_last_month', default=None, help='Where from continue the list')
@click.option('--month', default='next', help="Which month to print, can be 'current' or 'next'")
@click.option('--days_to_skip', 'days_to_skip_str', default=None,
              help="comma separated list of days to skip in the calendar")
@click.option('--saturdays_to_include', 'saturdays_to_include_str', default=None,
              help="comma separated list of saturdays to include in the calendar")
@click.option('--names_file', default='names.txt',
              help="File containing list of names, each one a line")
@click.option('--calendar_title', default='Fruit Calendar',
              help='alternate title of the calendar')
@click.option('--output_file', default='fcal-test.html',
              help='file to generate the calendar into')
@click.option('--config', 'config_file', default='fcal.yaml',
              help='path to fcal config file, storing holidays')
def print_calendar(last_name_of_last_month, month, days_to_skip_str,
                   saturdays_to_include_str, names_file, calendar_title,
                   output_file, config_file):
    """Prints a HTML calendar to the stdout
    Sample usage:
    python3 fcal.py --month next --last_name_of_last_month 'Ari Marcell'  --days_to_skip 2,5"""

    # Setup data
    nevek = [line.rstrip('\n') for line in open(names_file)]

    holidays, working_days = parse_config(config_file)

    loc = locale.getlocale() # get current locale

    fruit_calendar = calendar.LocaleHTMLCalendar(calendar.MONDAY, loc)
    next_names = get_next_name(nevek,
                               last_name_of_last_month)

    # TODO find a better name, like reference_date
    reference_date = TODAY

    if month == 'current':
        pass
    elif month == 'next':
        reference_date = add_months(TODAY, 1)
    else:
        raise Exception("Only values 'current and 'next' are accepted")

    if days_to_skip_str:
        holidays = holidays.union(parse_days(days_to_skip_str.split(","), month=reference_date.month))

    if saturdays_to_include_str:
        working_days = working_days.union(parse_days(saturdays_to_include_str.split(","), month=reference_date.month))

    html_str = fruit_calendar.formatmonth(reference_date.year, reference_date.month)

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

    for elem in root.findall("*//td"):
        if elem.get('class') != 'noday':
            dayno = elem.text
            day_elem = etree.SubElement(elem, "span")
            day_elem.attrib['class'] = 'day'
            day_elem.text = dayno
            elem.text = ''

            name = etree.SubElement(elem, "span")
            name.attrib['class'] = 'name'

            day = datetime.datetime(reference_date.year,
                                    reference_date.month,
                                    int(dayno))

            is_saturday = day.weekday() == 5

            if ((day in holidays) or
                    (is_saturday and
                     day not in working_days)):
                name.text = ""
                elem.set('class', 'holiday')
            else:
                name.text = next(next_names)

    body = etree.tostring(root, encoding="unicode")
    context = {
        'calendar_title': 'calendar_title',
        'body' : body
    }

    with open(output_file, "w") as target:
        output = render('./fcal.html', context)
        target.write(output)

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        sys.argv.append('--help')
     # pylint: disable=E1101,E1120
    print_calendar()
