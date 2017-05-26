import re
import sys
import json
import threading

from xmljson import abdera
from xml.etree.ElementTree import fromstring
from satori.rtm.client import make_client, SubscriptionMode
import satori.rtm.auth as auth


channel = "web-servers-online"
endpoint = "wss://open-data.api.satori.com"
appkey = ""
role = "web-servers-online"
secret = ""





def main():
    with make_client(endpoint=endpoint, appkey=appkey) as client:
        auth_finished_event = threading.Event()
        auth_delegate = auth.RoleSecretAuthDelegate(role, secret)

        def auth_callback(auth_result):
          if type(auth_result) == auth.Done:
              #print 'Auth success'
              auth_finished_event.set()
          else:
              #print 'Auth failure: {0}'.format(auth_result)
              sys.exit(1)

        client.authenticate(auth_delegate, auth_callback)

        if not auth_finished_event.wait(60):
            raise RuntimeError('Auth never finished')

        #print 'Subscribing to a channel'
        subscribed_event = threading.Event()
        got_message_event = threading.Event()

        class SubscriptionObserver(object):
            def on_enter_subscribed(self):
                subscribed_event.set()

            def on_subscription_data(self, data):
                for message in data['messages']:
                    pass
                    #print 'Client got message {0}'.format(message)
                got_message_event.set()

        subscription_observer = SubscriptionObserver()
        client.subscribe(channel,
          SubscriptionMode.SIMPLE,
          subscription_observer)

        if not subscribed_event.wait(10):
          #print "Couldn't establish the subscription in time"
          sys.exit(1)

        publish_finished_event = threading.Event()

        def publish_callback(ack):
            #print 'Publish ack:', ack
            publish_finished_event.set()

        while True:
            line = sys.stdin.readline()
            data = xmltodict.parse(data, dict_constructor=dict, attr_prefix='')
            if not line:
                break

            res = json.loads(line)
            up = res.get('success')
            if up:
                ip = res.get('saddr')
                port = res.get('sport')
                time = res.get('timestamp-str')
                loc = add_location(ip)
                msg = {'ip': ip, 'port': port, 'time': time}
                if loc:
                    msg.update(loc)

                open("/opt/zmap/ip.txt", "a").write(msg.get('ip')+'\n')

                client.publish(
                    channel, message=msg, callback=publish_callback)

        if not publish_finished_event.wait(10):
          #print "Couldn't publish the message in time"
          sys.exit(1)

        if not got_message_event.wait(10):
          #print "Couldn't receive the message in time"
          sys.exit(1)


if __name__ == '__main__':
    """
     zmap -p 80 -f "saddr,sport,success,timestamp-str" -O json -o - -n 1000 | python scripts/wsonline.py

    """
    #main()
    while True:
        packet = ''
        lines = sys.stdin.xreadlines()
        for line in lines:
            packet = packet + line
            print '\n\n\n\n', packet, '\n\n\n\n\n'
        # data = xmltodict.parse(line, dict_constructor=dict, attr_prefix='')
        # if not line:
        #     break
        #
        # res = json.loads(data)
        #print '\n\n\n\n', line, '\n\n\n\n\n'
