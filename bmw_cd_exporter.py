#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import core modules
import os
import sys
import requests
import time
import json
import argparse

# import the prometheus modules
import prometheus_client
from prometheus_client import start_http_server, Metric, REGISTRY, Gauge
from prometheus_client.core import GaugeMetricFamily

# import the bimmer_connected modules
import bimmer_connected
from bimmer_connected.account import ConnectedDriveAccount
from bimmer_connected.country_selector import get_region_from_name, valid_regions

DEBUG = int(os.environ.get('DEBUG', '0'))


class DataCollector(object):
    def __init__(self, user, password, region):
        self._user = user
        self._password = password
        self._region = region

    def _sanitise(self, string):
        return ''.join(e for e in string if e.isalnum())

    def collect(self):
        # set constants
        app = 'bmwconnecteddrive'
        json_filename = 'attributes.json'

        # connect to bmw
        account = ConnectedDriveAccount(self._user, self._password, get_region_from_name(self._region))
        if not account:
            print('ERROR: Unable to log on')
            exit(1)

        # update states of all vehicles
        account.update_vehicle_states()

        if DEBUG:
            print('Found {} vehicles: {}'.format(len(account.vehicles),','.join([v.name for v in account.vehicles])))

        # get attributes from json file
        with open(json_filename) as json_file:
            attrs = json.load(json_file)
            for vehicle in account.vehicles:
                for attr in attrs:
                    if getattr(vehicle.state,attr['name']):
                        vehicle_name = self._sanitise(vehicle.name)
                        metric_name = app + '_' + attr['name'] + '_' + attr['unit'] + '{vehicle="' + vehicle_name + '",vin="' + vehicle.vin + '"}'
                        yield GaugeMetricFamily(metric_name, attr['desc'], getattr(vehicle.state,attr['name']))


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
        '--region',
        metavar='rest_of_world',
        required=False,
        help='BMW Connected Drive region (north_america/china/rest_of_world)',
        default=os.environ.get('BMWCD_REGION','rest_of_world')
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

        # register & start prometheus exporter server
        REGISTRY.register(DataCollector(args.user, args.password, args.region))
        start_http_server(port)
        print("BMW Connected Drive exporter for Prometheus. Serving on port: {}".format(port))
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print('Keyboard interrupted. Exiting')
        exit(0)