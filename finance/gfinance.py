import csv
import time
import threading

from googlefinance import getQuotes
from satori.rtm.client import make_client
import satori.rtm.auth as auth


channel = "stock-quotes"
endpoint = "wss://open-data.api.satori.com"
appkey = ""
role = "stock-quotes"
secret = ""


def symbols(syml='nasdaq.csv'):
    with open(syml, 'rb') as f:
        symbols = csv.reader(f, delimiter=',', quotechar='"')
        for row in symbols:
            yield row[0]


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def data():
    for i in chunks([s for s in symbols()], 10):
        try:
            res = getQuotes(i)
            time.sleep(1)
            for i in res:
                yield i
        except Exception as e:
            print e

def main():
    with make_client(endpoint=endpoint, appkey=appkey) as client:
        auth_finished_event = threading.Event()
        auth_delegate = auth.RoleSecretAuthDelegate(role, secret)

        def auth_callback(auth_result):
            if type(auth_result) == auth.Done:
                auth_finished_event.set()

        client.authenticate(auth_delegate, auth_callback)

        if not auth_finished_event.wait(60):
            raise RuntimeError('Auth never finished')

        while True:
            for d in data():
                print d
                client.publish(channel, message=d)
                time.sleep(0.1)


if __name__ == '__main__':
    main()
