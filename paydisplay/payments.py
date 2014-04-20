#!/usr/bin/env python

import sys
import paydisplay.pd
import json

paydisplay.pd.get_config()

#print paydisplay.pd.CONFIG

def print_payment(payment):
    paydisplay.pd.disp(payment['description'])

    frequency = payment['frequency']
    frequency_str = ", ".join(map(str, frequency))
    freq_sequence = [i for i in xrange(*frequency)]

    print """Amount: %s
Frequency: xrange(%s) -> %s
Auxiliary rules: %s""" % (payment['amount'],
                          frequency_str,
                          freq_sequence,
                          str(payment['auxiliary_rules']))


for payment in paydisplay.pd.CONFIG['payments']:
    print_payment(payment)
