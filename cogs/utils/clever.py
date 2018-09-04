import requests
import json
import aiohttp
import asyncio

class CleverBot(object):
    def __init__(self, user, key, nick=None):
        self.user = user
        self.key = key
        self.nick = nick

        body = {
            'user': user,
            'key': key,
            'nick': nick
        }

        requests.post('https://cleverbot.io/1.0/create', json=body)

    async def query(self, text):
        body = {
            'user': self.user,
            'key': self.key,
            'nick': self.nick,
            'text': text
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.post('https://cleverbot.io/1.0/ask', json=body) as res:
                r = await res.json()
        # r = requests.post('https://cleverbot.io/1.0/ask', json=body)
        # r = json.loads(r.text)

        if r['status'] == 'success':
            return r['response']
        else:
            return False
