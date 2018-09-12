BMW Connected Drive exporter for Prometheus.io, written in Python 3.

This exporter uses [Gerard33's bimmer_connected library](https://github.com/gerard33/bimmer_connected), which is forked from [M1n3rva's](https://github.com/m1n3rva/bimmer_connected).

# Usage

## Arguments

    usage: bmw_cd_exporter.py [-h] [--user xxx@gmail.com] [--password abc123]
                        [--port 9488] [--region rest_of_world]

    BMW Connected Drive exporter for Prometheus available arguments:

    optional arguments:
    -h, --help            show this help message and exit
    --user xxx@gmail.com  Username (email address) for logging on to BMW
                          Connected Drive
    --password abc123     Password for logging on to BMW Connected Drive
    --port 9488           Exporter listens on this port
    --region rest_of_world
                          BMW Connected Drive region
                          (north_america/china/rest_of_world)
    --attributes attributes.json
                          Override path to the JSON file containing all 
                          attributes (optional)

## Environment Variables

The arguments can also be set as env variables instead. Useful if you're using it in a Docker container.
1. BMWCD_USER
2. BMWCD_PASSWORD
3. BMWCD_PORT
4. BMWCD_REGION

## Notes on Region

Note that the region must be one of the 3.
1. north_amercia
2. china
3. rest_of_world

The default is rest_of_world.

# Installation

## From Source

    git clone git@github.com:wywywywy/bmw_cd_exporter.git
    cd bmw_cd_exporter
    pip install -r requirements.txt

Use pip3 if your pip is for Python 2.

## With Docker

    docker run -d --restart=always -p 9488:9488 -e "BMWCD_USER=xxx@gmail.com" -e "BMWCD_PASSWORD=abc123" -e "BMWCD_REGION=rest_of_world" wywywywy/bmw_cd_exporter:latest

Change the environment variables to what you need.

## Prometheus Config

Add this to prometheus.yml and change the IP/port if needed.

    - job_name: 'bmw_cd_exporter'
        scrape_interval: 5m
        metrics_path: /
        static_configs:
        - targets:
            - '127.0.0.1:9488'

# Notes

It supports multiple vehicles in the same BMW Connected Drive account.

Please reduce the pooling rate to maybe once every minute, to avoid overloading BMW's servers.

Currently supported metrics are -
1. mileage
2. remaining_range_total
3. remaining_range_electric
4. remaining_range_fuel
5. remaining_fuel
6. charging_level_hv

If there's anything you want to add, let me know by submitting an issue, or just edit the JSON file directly.

The units seem to be in metric rather than imperial no matter where the vehicle is.

This obviously isn't endorsed by BMW, and they don't have a public API.  So they could make breaking changes any time.  Remember to not rely on this exporter for anything critical.

# TODO

1. ~~Docker~~
2. More metrics

# Contributing

Yes, contributions are always welcome.  
Fork it & submit a pull request.

# License

This is licensed under the Apache License 2.0.

# Disclaimer

This project is not affiliated with or endorsed by BMW Group.