#!/usr/bin/python
# Used to create and print xml elements https://pymotw.com/2/xml/etree/ElementTree/create.html
import requests
from datetime import datetime
import config
import nxtbus
import subprocess


def filter_buses(arrivals, allowed_buses, soonest_only=True):
    # only show allowed buses
    res = arrivals.copy()
    for bus, times in arrivals.iteritems():
        if int(bus) not in allowed_buses:
            del res[bus]
    return res


def display_bus_times(bus_stop, allowed_buses, special_text, color='cadetblue'):
    arrivals = None
    try:
        arrivals = nxtbus.bus_arrival_times(bus_stop)
    except Exception as e:
        print e
        print 'Failed to update | color=red'
        return
    if not arrivals:
        #print 'no buses soon | color=orange'
        return 
    arrivals = filter_buses(arrivals, allowed_buses)
    for bus, times in arrivals.iteritems():
        for time in times:
            timedelta = (time - datetime.now()).seconds / 60  # time delta in minutes
            if timedelta == 0:
                text = 'the {0} leaves {1} NOW'.format(bus, special_text)
            elif timedelta == 1:
                text = 'the {0} leaves {1} in 1 minute'.format(bus, special_text)
            else:
                text = 'the {0} leaves {1} in {2} minutes'.format(bus, special_text, timedelta)
            print text + ' | color=' + color


def main():
    for e in config.BUS_STOPS:
        stopid = e['stopid']
        alias = e['alias']
        buses = e['buses']
        display_bus_times(stopid, buses, alias)


if __name__ == '__main__':
    main()
