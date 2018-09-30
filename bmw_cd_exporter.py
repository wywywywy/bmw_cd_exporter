#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import core modules
import os
import sys
import time
import json
import argparse

# import the prometheus modules
import prometheus_client
from prometheus_client import start_http_server, Gauge

# import the bimmer_connected modules
import bimmer_connected
from bimmer_connected.account import ConnectedDriveAccount
from bimmer_connected.country_selector import get_region_from_name, valid_regions

# initial values
DEBUG = int(os.environ.get('DEBUG', '0'))
gauges = {}
attrs = {}
app = 'bmwconnecteddrive'

# collect data from BMW CD
def collectData(user, password, region, attributes):
    # connect to bmw
    account = ConnectedDriveAccount(user, password, get_region_from_name(region))
    if not account:
        print('ERROR: Unable to log on')
        exit(1)

    # update states of all vehicles
    account.update_vehicle_states()

    if DEBUG:
        print('DEBUG: Found {} vehicles: {}'.format(len(account.vehicles),','.join([v.name for v in account.vehicles])))

    # set gauges for each vehicle
    for vehicle in account.vehicles:
        for attr in attrs:
            if getattr(vehicle.state,attr['name']):
                vehicle_name = ''.join(e for e in vehicle.name if e.isalnum())
                if gauges[attr['name']]:
                    gauges[attr['name']].labels(vehicle=vehicle_name, vin=vehicle.vin).set(getattr(vehicle.state,attr['name']))


def parse_args():
    parser = argparse.ArgumentParser(
        description='BMW Connected Drive exporter for Prometheus available arguments:'
    )
    parser.add_argument(
        '--user',
        metavar='xxx@gmail.com',
        required=False,
        help='Username (email address) for logging on to BMW Connected Drive',
        default=os.environ.get('BMWCD_USER')
    )
    parser.add_argument(
        '--password',
        metavar='abc123',
        required=False,
        help='Password for logging on to BMW Connected Drive',
        default=os.environ.get('BMWCD_PASSWORD')
    )
    parser.add_argument(
        '--port',
        metavar='9488',
        required=False,
        type=int,
        help='Exporter listens on this port',
        default=int(os.environ.get('BMWCD_PORT', '9488'))
    )
    parser.add_argument(
        '--interval',
        metavar='5',
        required=False,
        type=int,
        help='Pooling interval in minutes',
        default=int(os.environ.get('BMWCD_INTERVAL', '5'))
    )
    parser.add_argument(
        '--region',
        metavar='rest_of_world',
        required=False,
        help='BMW Connected Drive region (north_america/china/rest_of_world)',
        default=os.environ.get('BMWCD_REGION','rest_of_world')
    )
    parser.add_argument(
        '--attributes',
        metavar='attributes.json',
        required=False,
        help='Override path to the JSON file containing all attributes (optional)',
        default='attributes.json'
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        # get & check args
        args = parse_args()
        port = int(args.port)
        if not args.user:
            print('ERROR: Invalid user')
            exit(1)
        elif not args.password:
            print('ERROR: Invalid password')
            exit(1)
        elif not args.region:
            print('ERROR: Invalid region')
            exit(1)
        if args.interval < 1:
            args.interval = 1

        # register & start prometheus exporter server
        print('INFO: Registering Prometheus metrics...')
        with open(args.attributes) as json_file:
            attrs = json.load(json_file)
            for attr in attrs:
                gauges[attr['name']] = Gauge(app + '_' + attr['name'] + '_' + attr['unit'], attr['desc'], ['vehicle','vin'])

        # Get initial metrics
        print('INFO: Getting data from BMW Connected Drive...')
        collectData(args.user, args.password, args.region, args.attributes)

        # Start HTTP server
        print('INFO: Starting HTTP server...')
        start_http_server(port)
        print("INFO: BMW Connected Drive exporter for Prometheus. Serving on port: {}".format(port))
        while True: 
            time.sleep(args.interval * 60)
            collectData(args.user, args.password, args.region, args.attributes)

    except KeyboardInterrupt:
        print('INFO: Keyboard interrupted. Exiting')
        exit(0)