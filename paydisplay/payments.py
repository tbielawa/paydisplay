#!/usr/bin/env python

import sys
import paydisplay.pd
import json

paydisplay.pd.get_config()

def frequency(payment):
    pay_month = payment.get('month', '*')
    pay_day = payment.get('day', '1')
    return (pay_month, pay_day)

def print_payment(payment):
    paydisplay.pd.disp(payment['description'])
    (pay_month, pay_day) = frequency(payment['frequency'])
    amount = payment['amount']
    heat_colors = paydisplay.pd.CONFIG['config']['heat_colors']
    payment_color = 'white'
    for color, range in heat_colors.iteritems():
        if range[0] <= amount <= range[1]:
            payment_color = color

    _amount = "{:.2f}".format(payment['amount'])

    print """Amount: %s
Frequency (MM-DD): %s-%s
""" % (paydisplay.pd.colorize(payment_color, _amount),
       pay_month,
       pay_day)



payments = paydisplay.pd.CONFIG['payments']
#for payment in paydisplay.pd.CONFIG['payments']:
for payment in sorted(payments, key=lambda x: x['frequency']['day']):
    print_payment(payment)
