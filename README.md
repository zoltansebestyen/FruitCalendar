This little tool aims to generate a printable 'Fruit Calendar'
with the name of a member of the group for each work day.

Essentially it's a rota calendar generator for kindergarten and because of that,
it's rather static: does not store the rota in a database and supposed to run
once a month.

Usage:
You have to have a file with the list of names (separated by newline)
to fill the calendar with.
You can specify which month's calendar you want: current or next,
depending on when you generate it (before end of month or after).
Also, you're supposed to tell the last name used for the previous calendar so
that this tool can continue with the next one.
But just run 'fcal.py --help for' the actual list of options.

Here's an example to generate a fruit calendar:

```
./fcal.py --month current --names_file names.txt --last_name_of_last_month \
"Frodo Gamgee" --calendar_title "Fruit Calendar" > 2018-feb.html
```

Optionally you can skip selected days from the calendar ( a dash will be
inserted for that date ) and add working Saturdays to the calendar:

```
./fcal.py --month current --names_file names.txt --last_name_of_last_month \
"Frodo Gamgee" --calendar_title "Fruit Calendar" \
--days_to_skip 15,16 --saturdays_to_include 10 > 2018-feb.html
```
