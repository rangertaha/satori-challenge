import sys
import time
import json
import datetime
import threading

import pytz
import requests
import pandas

from satori.rtm.client import make_client
import satori.rtm.auth as auth


channel = "air-traffic"
endpoint = "wss://open-data.api.satori.com"
appkey = "8aDF97c4CC03d0FF8508351CBE3Edab3"
role = "air-traffic"
secret = "A9639B1C5a3BF30CCF9eeeBdF73B2aF8"


def get_data():
    r = requests.get('https://planefinder.net/endpoints/update.php')
    row = {}
    data = r.json()
    planes = data['planes']
    keys = planes.keys()
    for a in keys:
        for b in planes[a].keys():
            row = {
                'id': b,
                'list': planes[a].keys(),
            }

    df = pandas.DataFrame(planes['0'])
    ndf = df.transpose()

    ndf.columns = ["aircraft", "flight", "callsign", "lat", "lon", "altitude",
                   "course", "speed", "time", "9", 'flight_no', 'origin-dest',
                   "13"]
    o = ndf
    o['time'] = o['time'].apply(_time)
    o['time'] = pandas.to_datetime(o.time)
    o = o.sort_values(by='time')
    o['origin'] = o['origin-dest'].apply(_origin)
    o['destination'] = o['origin-dest'].apply(_destination)
    del o['origin-dest']
    del o['13']
    return o


def _time(t):
    return datetime.datetime.fromtimestamp(
        int(t), pytz.utc).strftime('%Y-%m-%d %H:%M:%S')


def _origin(od):
    return od[:3]


def _destination(od):
    return od[len(od) - 3:]


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
            print('Publish ack:', ack)

        while True:
            # Downloads the data every 40 seconds
            data = get_data()
            for i, r in data.iterrows():
                time.sleep(0.005)
                msg = json.loads(r.to_json())
                client.publish(
                    channel, message=msg, callback=publish_callback)


if __name__ == '__main__':
    main()
