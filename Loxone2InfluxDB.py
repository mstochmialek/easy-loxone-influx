#!/usr/bin/python

# Simple script to import Loxone UDP logs into InfluxDB
import os
import socket
import json
import argparse
import logging
from influxdb import InfluxDBClient
from datetime import datetime
from dateutil import tz
# suppress warnings for unverified https request
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============== Configuration =====================
# hostname and port of InfluxDB http API
host = os.getenv('INFLUXDB_HOST', '127.0.0.1')
port = int(os.getenv('INFLUXDB_PORT', 8086))
# use https for connection to InfluxDB
ssl = bool(os.getenv('INFLUXDB_HTTPS', False))
# verify https connection
verify = bool(os.getenv('INFLUXDB_VERIFY_HTTPS', False))
# InfluxDB database name
dbname = os.getenv('INFLUXDB_DATABASE', 'loxone')
# InfluxDB login credentials (optional, specify if you have enabled authentication)
dbuser = os.getenv('INFLUXDB_USER')
dbuser_code = os.getenv('INFLUXDB_PASSWORD')
# local IP and port where the script is listening for UDP packets from Loxone
localIP = os.getenv('BIND_ADDRESS', '0.0.0.0')
localPort = int(os.getenv('BIND_PORT', 2222))


def parse_log_data(data, from_zone, to_zone, debug=False):
    """
    Parse received message
    Syntax: <timestamp>;<measurement_name>;<alias(optional)>:<value>;<tag_1(optional)>;<tag_2(optional)>;<tag_3(optional)>
    Example: "2020-09-10 19:46:20;Bedroom temperature;23.0"
    ** TO DO ** Need to add checks in case something goes wrong
    """
    logging.debug('Received: %s', data)

    chunks = data.split(';')

    # Timestamp Extraction
    timestamp_str = chunks[0].replace(' ', 'T') + 'Z'
    # Timezone conversion to UTC
    timestamp_local = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
    timestamp_utc = timestamp_local.replace(tzinfo=from_zone).astimezone(to_zone)
    timestamp = timestamp_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    name = chunks[1]

    value_chunks = chunks[2].split(':', 2)
    has_alias = len(value_chunks) > 1
    if has_alias:
        name = value_chunks[0]
        value = value_chunks[1]
    else:
        value = value_chunks[0]

    # Tags Extraction
    tag1 = parse_tag(chunks[3], 'Tag_1') if len(chunks) > 3 else {}
    tag2 = parse_tag(chunks[4], 'Tag_2') if len(chunks) > 4 else {}
    tag3 = parse_tag(chunks[5], 'Tag_3') if len(chunks) > 5 else {}

    # Create Json body for Influx
    json_body = [
        {
            "measurement": name,
            "tags": tag1 | tag2 | tag3 | {"Source": "Loxone"},
            "time": timestamp,
            "fields": {
                "value": float(value)
            }
        }
    ]

    if debug:
        logging.debug(json.dumps(json_body, indent=2))

    return json_body


def parse_tag(tag_str, default_key):
    tag_chunks = tag_str.split(':', 2)
    if len(tag_chunks) > 1:
        tag_key = tag_chunks[0]
        tag_val = tag_chunks[1]
    else:
        tag_key = default_key
        tag_val = tag_chunks[0]
    return {tag_key.strip(): tag_val.strip()}


def main(host, port, ssl, verify, debug=False):
    """Instantiate a connection to the InfluxDB and stard listening on UDP port for incoming messages"""

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s %(levelname)s - %(message)s')
    logging.info('Creating InfluxDB client - connection: %s:%s, db: %s', host, port, dbname)

    client = InfluxDBClient(host, port, dbuser, dbuser_code, dbname, ssl, verify)

    # get TZ info
    to_zone = tz.tzutc()
    from_zone = tz.tzlocal()

    # A UDP server
    # Set up a UDP server
    logging.info('Listening for incoming Loxone UDP packets on %s:%s', localIP, localPort)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Listen on local port
    # (to all IP addresses on this system)
    listen_addr = (localIP, localPort)
    udp_sock.bind(listen_addr)
    logging.debug('Socket attached')

    # Report on all data packets received and
    # where they came from in each case (as this is
    # UDP, each may be from a different source and it's
    # up to the server to sort this out!)
    while True:
        data, addr = udp_sock.recvfrom(1024)
        json_body_log = parse_log_data(data.decode('utf-8'), from_zone, to_zone, debug)
        # Write to influx DB
        client.write_points(json_body_log)


def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        add_help=False, description='Simple Loxone to InfluxDB script')
    parser.add_argument('-h', '--host', type=str, required=False,
                        default=host,
                        help='hostname of InfluxDB http API')
    parser.add_argument('-p', '--port', type=int, required=False, default=port,
                        help='port of InfluxDB http API')
    parser.add_argument('-s', '--ssl', default=ssl, action="store_true",
                        help='use https to connect to InfluxDB')
    parser.add_argument('-v', '--verify', default=verify, action="store_true",
                        help='verify https connection to InfluxDB')
    parser.add_argument('-d', '--debug', action="store_true", default=bool(os.getenv('DEBUG', False)),
                        help='debug code')
    parser.add_argument('-?', '--help', action='help',
                        help='show this help message and exit')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port, ssl=args.ssl, verify=args.verify, debug=args.debug)
