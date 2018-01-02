import calendar

c = calendar.HTMLCalendar(calendar.MONDAY)

str = c.formatmonth(2018, 1)
print(str)
