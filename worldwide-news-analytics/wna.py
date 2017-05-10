"""

"""
import json
import time
import threading

import redis
from satori.rtm.client import make_client
import satori.rtm.auth as auth

redis_host = '127.0.0.1'
channel = "worldwide-news-analysis"
endpoint = "wss://open-data.api.satori.com"
appkey = "8aDF97c4CC03d0FF8508351CBE3Edab3"
role = "worldwide-news-analysis"
secret = "d5e4E6ddFdb275eaFc54df5Ff9e7f182"



def main():
    WAIT_TIME = 0
    with make_client(endpoint=endpoint, appkey=appkey) as client:
        redis_con = redis.StrictRedis(
            host=redis_host,
            port=6379,
            db=0)
        auth_finished_event = threading.Event()
        auth_delegate = auth.RoleSecretAuthDelegate(role, secret)

        def auth_callback(auth_result):
            if type(auth_result) == auth.Done:
                auth_finished_event.set()

        client.authenticate(auth_delegate, auth_callback)

        if not auth_finished_event.wait(60):
            raise RuntimeError('Auth never finished')

        while True:
            # Get article from redis queue and push to satori
            item = redis_con.lpop('articles:items')
            if item:
                WAIT_TIME = 0
                obj = json.loads(item)
                if obj.get('text'):
                    # delete the body of the article
                    del obj['text']
                    client.publish(
                        channel, message=obj)
            else:
                WAIT_TIME += 1
                time.sleep(WAIT_TIME)

if __name__ == '__main__':
    main()
