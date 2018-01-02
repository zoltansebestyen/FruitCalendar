import calendar
import xml.etree.ElementTree as etree
import sys

nevek = [line.rstrip('\n') for line in open('nevek.txt')]

last_name_of_last_month = None

if len(sys.argv) > 1:
    last_name_of_last_month = sys.argv[1]

def get_next_name():
    if last_name_of_last_month is not None and \
        last_name_of_last_month in nevek:
        offset = nevek.index(last_name_of_last_month)
    else:
        offset = 0

    # Should be 31
    for x in range(31):
        yield str(nevek[( x + offset) % len (nevek)])

    # FIXME to circumvent iteration errors
    for x in range(100):
        yield "-"

c = calendar.HTMLCalendar(calendar.MONDAY)
n = get_next_name()

htmlStr = c.formatmonth(2018, 1)
# print(str)

htmlStr = htmlStr.replace("&nbsp;"," ")

root = etree.fromstring(htmlStr)
for elem in root.findall("*//td"):
    # if elem.get("class") != "tue":
    #     continue
    # elem.text += "!"

    br = etree.SubElement(elem, "br")
    br.tail = n.next()
    print (elem.text + str(br.tail))

print etree.tostring(root, encoding='utf-8')
