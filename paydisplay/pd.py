#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright © 2014 Tim Bielawa <timbielawa@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import json
from pprint import pprint as pp
import datetime
import calendar


CONFIG = {}
BG = {}
BG['BLACK'] = '\033[40m'
BG['RED'] = '\033[41m'
BG['GREEN'] = '\033[42m'
BG['YELLOW'] = '\033[43m'
BG['BLUE'] = '\033[44m'
BG['PURPLE'] = '\033[45m'
BG['CYAN'] = '\033[46m'
BG['LIGHTGRAY'] = '\033[47m'
COLORS = {}
COLORS['RESTORE'] = '\033[0m'
COLORS['RED'] = '\033[00;31m'
COLORS['GREEN'] = '\033[00;32m'
COLORS['YELLOW'] = '\033[00;33m'
COLORS['BLUE'] = '\033[00;34m'
COLORS['PURPLE'] = '\033[00;35m'
COLORS['CYAN'] = '\033[00;36m'
COLORS['TEAL'] = '\033[00;36m'
COLORS['LIGHTGRAY'] = '\033[00;37m'
COLORS['LRED'] = '\033[01;31m'
COLORS['LGREEN'] = '\033[01;32m'
COLORS['LYELLOW'] = '\033[01;33m'
COLORS['LBLUE'] = '\033[01;34m'
COLORS['LPURPLE'] = '\033[01;35m'
COLORS['LCYAN'] = '\033[01;36m'
COLORS['WHITE'] = '\033[01;37m'

HEAT_COLOR_ORDER = ['RED', 'YELLOW', 'GREEN', 'BLUE', 'CYAN', 'PURPLE']

def frequency(payment):
    pay_month = payment['frequency'].get('month', '*')
    pay_day = payment['frequency'].get('day', '1')
    return (pay_month, pay_day)

def print_payment(payment):
    disp(payment['description'], color='lblue', underline=True)
    (pay_month, pay_day) = frequency(payment)
    amount = payment['amount']
    heat_colors = CONFIG['config']['heat_colors']
    payment_color = 'white'
    for color, range in heat_colors.iteritems():
        if range[0] <= amount <= range[1]:
            payment_color = color

    _amount = "{:.2f}".format(payment['amount'])

    print """Amount: %s
Frequency (MM-DD): %s-%s
""" % (colorize(payment_color, _amount),
       pay_month,
       pay_day)

def sum_daily_payments(to_pay, day_of_month):
    """'to_pay' is as in 'sum_monthly_payments', 'day_of_month' is an
integer of the day of the month a summary is requested for"""
    payments = to_pay.get(day_of_month, [{'amount': 0}])
    _payments = map(lambda x: x['amount'], payments)
    return sum(_payments)

def sum_monthly_payments(to_pay):
    """'to_pay' should be a dict where keys = days of the month and values
= list of payments on that day"""
    sum = 0
    for day, payments in to_pay.iteritems():
        #disp("Day: %s" % day)
        #print "# Payments: %s" % len(payments)
        for p in payments:
            sum += p['amount']
    return sum

def get_pay_schedule(to_pay):
    pay_schedule = {}
    for payment in to_pay:
        pay_month, pay_day = frequency(payment)
        payments_on_day = pay_schedule.get(pay_day, [])
        payments_on_day.append(payment)
        pay_schedule.update({pay_day: payments_on_day})
    return pay_schedule

def print_schedule(to_pay):
    disp('Scheduled Payments', color='green')
    for payment in sorted(to_pay, key=lambda x: x['frequency']['day']):
        print_payment(payment)


def get_config():
    config_locations = [".paydisplay.json", "paydisplay.json", os.path.expanduser("~/.paydisplay.json")]
    for location in config_locations:
        if os.path.exists(location):
            print "Using config: %s" % location
            c = json.loads(open(location, 'r').read())
            break

    global CONFIG
    CONFIG = c
    return c

def print_heat_bar():
    color_strs = [colorize('white', " X ", background='black')]
    i = 0
    for color in HEAT_COLOR_ORDER:
        color_strs.append(colorize('white', " %s " % i, background=color))
        i += 1
    print "".join(color_strs)


def heat_background(day, month_sum):
    """Give 'day' as the total amount of payments on that day. 'month_sum'
is the sum for the month"""
    # These are ordered from coolest to hottest
    HEAT_COLOR_ORDER = ['RED', 'YELLOW', 'GREEN', 'BLUE', 'CYAN', 'PURPLE']
    inc = range(1, 101, 15)
    day_pct = 100 * (day/float(month_sum))
    #disp("Day Payments %s | Day Percent: %s | Month Total: %s" % (day,
    #                                                    day_pct,
    #                                                    month_sum))
    if day == 0:
        #print "BLACK!"
        return 'BLACK'
    else:
        if 0 < day_pct <= inc[1]:
            #print "%s <= %s <= %s" % (inc[0], day_pct, inc[1])
            return HEAT_COLOR_ORDER[0]
        elif inc[1] <= day_pct <= inc[2]:
            #print "%s <= %s <= %s" % (inc[1], day_pct, inc[2])
            return HEAT_COLOR_ORDER[1]
        elif inc[2] <= day_pct <= inc[3]:
            #print "%s <= %s <= %s" % (inc[2], day_pct, inc[3])
            return HEAT_COLOR_ORDER[2]
        elif inc[3] <= day_pct <= inc[4]:
            #print "%s <= %s <= %s" % (inc[3], day_pct, inc[4])
            return HEAT_COLOR_ORDER[3]
        elif inc[4] <= day_pct <= inc[5]:
            #print "%s <= %s <= %s" % (inc[4], day_pct, inc[5])
            return HEAT_COLOR_ORDER[4]
        else:
            #print "%s <= %s" % (inc[5], day_pct)
            return HEAT_COLOR_ORDER[5]

        #while i < len(heat_borders):
        # each item is the number from 1->100% that indicates a
        # color change. '1' implicitly changes from 0=black to
        # 1=RED
        #print "loop: %s" % i
        # if i == len(heat_borders) - 1:
        #     #print "heat order: %s" % heat_order[i-1]
        #     return heat_order[i-1]
        # else:
        #     if heat_borders[i] <= day_pct < heat_borders[i+1]:
        #         #print "heat order: %s" % heat_order[i]
        #         return heat_order[i]
        #     else:
        #         #print "%s <= %s < %s" % (heat_borders[i], day_pct,  heat_borders[i+1])
        #         pass

        # i += 1


def disp(item, color='red', underline=False):
    _prefix = colorize('white', 'Displaying: ')
    _item = colorize(color, item, underline=underline)
    print "%s%s" % (_prefix, _item)

def colorize(color, item, underline=False, background=None):
    if underline:
        ul = "\033[4m"
    else:
        ul = ''

    if background:
        bg = BG[background.upper()]
    else:
        bg = BG['BLACK']
    return "%s%s%s%s%s%s" % (COLORS['RESTORE'],
                             COLORS[color.upper()],
                             bg, ul, item,
                             COLORS['RESTORE'])

def help():
    print """
d|display - display calendar
c|config - display config
h|help - help
q|quit - quit"""

def repl():
    print colorize('yellow', "Enter 'h' or 'help' to see commands available")
    while True:
        display_calendar()
        sys.exit(0)
        cmd = raw_input('command: ')
        if cmd == 'd' or cmd == 'disp':
            disp('Calendar')
            display_calendar()
        elif cmd == 'c' or cmd == 'config':
            disp('Config')
            display_config()
        elif cmd == 'q' or cmd == 'quit':
            disp('QUIT')
            break
        else:
            disp('HELP')
            help()


    sys.exit(0)

def display_config():
    print(json.dumps(CONFIG, indent=4))


def display_week(day, color_day=None):
    # By default, colorize 'today' in the week. But if 'color_day' is
    # given, only colorize days that match 'color_day'. If no days
    # match, nothing is colored.
    #
    # TODO: Change 'color_day' to 'underline_day' or something. We
    # originally colored the given day if it was displayed on the
    # calendar, but now we underline it instead. See 'display_week'.
    if not color_day:
        color_day = day

    if day.weekday() == 6:
        dow = 0
    else:
        # The +1 accounts for days starting on monday
        dow = day.isoweekday()
    #disp('Weekday: %s' % colorize('green', dow))
    one_day = datetime.timedelta(days=1)

    # Weeks start on sunday
    sunday = day - (one_day * dow)
    # Collect the items to print for this week
    week_days = []

    payments = get_pay_schedule(CONFIG['payments'])
    #print payments
    month_total = sum_monthly_payments(payments)
    #print month_total

    for i in xrange(7):
        day_to_show = sunday + (one_day * i)
        daily_payment = sum_daily_payments(payments, day_to_show.day)
        _bg = heat_background(daily_payment, month_total)
        if day_to_show.day == color_day.day:
            week_days.append(colorize('white',
                                      str(day_to_show.day).zfill(2),
                                      underline=True,
                                      background=_bg))
        else:
            if day_to_show.month != color_day.month:
                week_days.append(colorize('lightgray',
                                          str(day_to_show.day).zfill(2)))
            else:
                week_days.append(colorize('white',
                                          str(day_to_show.day).zfill(2),
                                          background=_bg))

    print " %s  %s  %s  %s  %s  %s  %s " % tuple(map(lambda x: str(x).zfill(2), week_days))


def display_month(start_day):
    # Get the first day of the month by finding what the current day
    # is. Get this from day.day.
    day = datetime.timedelta(days=1)
    first_day = datetime.datetime(start_day.year, start_day.month, 1)
    days_in_month = calendar.monthrange(start_day.year, start_day.month)[1]
    i = 0
    print_heat_bar()
    while i < days_in_month:
        day_diff = (day * i)
        display_week(first_day + day_diff, color_day=start_day)
        i += 7

def display_year(day):
    pass

def display_calendar():
    # First, display today
    today = datetime.datetime.now()
    disp('Today: %s' % colorize('yellow', today.day))
    # Then display this week
    display_week(today)
    # Then display this month
    disp("Month")
    display_month(today)
    # Then display this year
    disp("Year")
    display_year(today)

def main():
    get_config()
    result = repl()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt, e:
        pass

    #     print e
    #     import pdb
    #     pdb.set_trace()
