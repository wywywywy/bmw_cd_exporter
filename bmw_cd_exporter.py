#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import core modules
import os
import time
import json
import argparse
import asyncio

# import the prometheus modules
from prometheus_client import start_http_server, Gauge

# import the bimmer_connected modules
from bimmer_connected.account import MyBMWAccount
from bimmer_connected.api.regions import get_region_from_name
from bimmer_connected.models import ValueWithUnit

# initial values
DEBUG = int(os.environ.get('DEBUG', '0'))
gauges = {}
attrs = {}
app = 'bmwconnecteddrive'

# collect data from BMW CD
async def collectData(user, password, region, attributes):
    # connect to bmw
    account = MyBMWAccount(user, password, get_region_from_name(region))
    if not account:
        print('ERROR: Unable to log on')
        exit(1)

    # update states of all vehicles
    await account.get_vehicles()

    if DEBUG:
        print('DEBUG: Found {} vehicles: {}'.format(len(account.vehicles),','.join([v.name for v in account.vehicles])))

    # set gauges for each vehicle
    for vehicle in account.vehicles:
        vehicle_name = ''.join(e for e in vehicle.name if e.isalnum())
        for attr in attributes:
            if attr['group']:
                vehicle_attribute_group = getattr(vehicle.status.vehicle,attr['group'])
                vehicle_attribute = getattr(vehicle_attribute_group,attr['name'])
            else:
                vehicle_attribute = getattr(vehicle.status.vehicle,attr['name'])
            if vehicle_attribute:
                if type(vehicle_attribute) == ValueWithUnit: # some attributes are typed ValueWithUnit, some are just numbers
                    vehicle_attribute_value = vehicle_attribute.value
                else:
                    vehicle_attribute_value = vehicle_attribute
                if type(vehicle_attribute_value) == int or type(vehicle_attribute_value) == float:
                    gauge = gauges[attr['name']]
                    if gauge:
                        gauge.labels(vehicle=vehicle_name, vin=vehicle.vin).set(vehicle_attribute_value)


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
        help='Polling interval in minutes',
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


async def main():
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
        await collectData(args.user, args.password, args.region, attrs)

        # Start HTTP server
        print('INFO: Starting HTTP server...')
        start_http_server(port)
        print("INFO: BMW Connected Drive exporter for Prometheus. Serving on port: {}".format(port))
        while True: 
            time.sleep(args.interval * 60)
            await collectData(args.user, args.password, args.region, attrs)

    except KeyboardInterrupt:
        print('INFO: Keyboard interrupted. Exiting')
        exit(0)


asyncio.run(main())