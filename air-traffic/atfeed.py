
#from __future__ import print_function
import sys
import time
import datetime
import threading


import pytz
import requests
import pandas


from satori.rtm.client import make_client, SubscriptionMode
import satori.rtm.auth as auth

#https://planefinder.net//api/api.php?r=metadata


r = requests.get('https://planefinder.net/endpoints/update.php')

r.status_code

r.headers['content-type']


r.encoding


r.text

d = {}
data = r.json()
planes = data['planes']
keys = planes.keys()
for a in keys:
    for b in planes[a].keys():
        row = {
            'id': b,
            'list': planes[a].keys(),
        }
        d = row

df = pandas.DataFrame(planes['0'])

ndf = df.transpose()

ndf.columns = ["aircraft", "flight", "callsign", "lat", "lon", "altitude",
    "course", "speed", "time", "9", 'flight_no', 'origin-dest', "13"]

o = ndf


def _time(t):
    return datetime.datetime.fromtimestamp(
        int(t), pytz.utc).strftime('%Y-%m-%d %H:%M:%S')


def _origin(od):
    return od[:3]


def _destination(od):
    return od[len(od)-3:]


o['time'] = o['time'].apply(_time)

o['time'] = pandas.to_datetime(o.time)
o = o.sort_values(by='time')


#o['origin'] = ''
o['origin'] = o['origin-dest'].apply(_origin)
o['destination'] = o['origin-dest'].apply(_destination)
del o['origin-dest']
del o['13']









channel = "air-traffic"
endpoint = "wss://open-data.api.satori.com"
appkey = "8aDF97c4CC03d0FF8508351CBE3Edab3"
role = "air-traffic"
secret = "A9639B1C5a3BF30CCF9eeeBdF73B2aF8"

def main():
    with make_client(endpoint=endpoint, appkey=appkey) as client:
        auth_finished_event = threading.Event()
        auth_delegate = auth.RoleSecretAuthDelegate(role, secret)

        def auth_callback(auth_result):
          if type(auth_result) == auth.Done:
              #print('Auth success')
              auth_finished_event.set()
          else:
              #print('Auth failure: {0}'.format(auth_result))
              sys.exit(1)

        client.authenticate(auth_delegate, auth_callback)

        if not auth_finished_event.wait(60):
          raise RuntimeError('Auth never finished')

        print('Subscribing to a channel')
        subscribed_event = threading.Event()
        got_message_event = threading.Event()

        class SubscriptionObserver(object):
          def on_enter_subscribed(self):
              subscribed_event.set()

          def on_subscription_data(self, data):
              for message in data['messages']:
                  #print('Client got message {0}'.format(message))
                  pass
              got_message_event.set()

        subscription_observer = SubscriptionObserver()
        client.subscribe(channel,
          SubscriptionMode.SIMPLE,
          subscription_observer)

        if not subscribed_event.wait(10):
          #print("Couldn't establish the subscription in time")
          sys.exit(1)

        publish_finished_event = threading.Event()

        def publish_callback(ack):
          #print('Publish ack:', ack)
          publish_finished_event.set()

        for i, r in o.iterrows():
            time.sleep(0.01)
            #print r.to_json()
            client.publish(
                channel, message=r.to_json(), callback=publish_callback)



        if not publish_finished_event.wait(10):
          #print("Couldn't publish the message in time")
          sys.exit(1)

        if not got_message_event.wait(10):
          #print("Couldn't receive the message in time")
          sys.exit(1)

if __name__ == '__main__':
    while True:
        main()

