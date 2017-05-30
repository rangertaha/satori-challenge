#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""


"""
import sys
import time
import threading

import requests
from satori.rtm.client import make_client
import satori.rtm.auth as auth


channel = "air-traffic"
endpoint = "wss://open-data.api.satori.com"
appkey = "8aDF97c4CC03d0FF8508351CBE3Edab3"
role = "air-traffic"
secret = "A9639B1C5a3BF30CCF9eeeBdF73B2aF8"


def get_data():
    results = []
    r = requests.get(
        'https://data-live.flightradar24.com/zones/fcgi/feed.js'
        '?bounds=83.68,-72.22,-264.73,264.73&faa=1&mlat=1&flarm=1'
        '&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&maxage=7200&gli'
        'ders=1&stats=1', headers={'User-Agent': 'Mozilla/4.0 (comp'
            'atible; MSIE 6.0; Windows NT 5.1; FSL 7.0.6.01001)'})
    data = r.json()

    for key in data.keys():
        if isinstance(data[key], list):
             yield {
                'lat': data[key][1],
                'lon': data[key][2],
                'course': data[key][3],
                'altitude': data[key][4],
                'speed': data[key][5],
                'aircraft': data[key][8],
                'registration': data[key][9],
                'time': data[key][10],
                'origin': data[key][11],
                'destination': data[key][12],
                'flight': data[key][13],
                'callsign': data[key][16]
            }

def main():
    with make_client(endpoint=endpoint, appkey=appkey) as client:
        auth_finished_event = threading.Event()
        auth_delegate = auth.RoleSecretAuthDelegate(role, secret)

        def auth_callback(auth_result):
            if type(auth_result) == auth.Done:
                print('Auth success')
                auth_finished_event.set()
            else:
                print('Auth failure: {0}'.format(auth_result))
                sys.exit(1)

        client.authenticate(auth_delegate, auth_callback)

        def publish_callback(ack):
            #print('Publish ack:', ack)
            pass

        while True:
            data = get_data()
            for i in get_data():
                print i
                client.publish(
                    channel, message=i, callback=publish_callback)
                time.sleep(0.001)

if __name__ == '__main__':
    main()
