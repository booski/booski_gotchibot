#!/usr/bin/env python3

import requests
import json
import os
import pickle
from time import sleep
from classes import Gotchi


### Declarations ###

class Main:
    def __init__(self, token, gotchis):
        self.token = token
        self.gotchis = gotchis
        self.update_offset = 0
        
        self.url = 'https://api.telegram.org/bot%s/' % token
        self.geturl = '%sgetUpdates' % self.url
        self.sendurl = '%ssendMessage' % self.url


    def tick(self):
        dead_gotchis = list()
        for gotchi_id in self.gotchis:
            gotchi = self.gotchis[gotchi_id]
            if gotchi._isalive():
                out = gotchi._tick()
                if out != None:
                    self.send(gotchi_id, out)

            else:
                dead_gotchis.append(gotchi_id)

        for gotchi_id in dead_gotchis:
            del self.gotchis[gotchi_id]

        result = self.receive()
        
        if result['ok'] == True:
            updates = result['result']
            for update in updates:
                self.handle_update(update)

        else:
            print(result)


    def handle_update(self, update):
        self.update_offset = update['update_id'] + 1
        if 'message' in update:
            message = update['message']
            text = message['text']
            gotchi_id = message['chat']['id']
            
            result = None
            if gotchi_id in self.gotchis:
                result = self.gotchis[gotchi_id]._react(normalize(text))
            else:
                result = self.gotchi_init(gotchi_id, normalize(text))

            if result != None:
                self.send(gotchi_id, result)
            else:
                print("Missing answer for: '%s'" % message)
    
    
    def gotchi_init(self, gotchi_id, message):
        if message == 'start':
            self.gotchis[gotchi_id] = Gotchi()
            return "You've found a gotchi egg!"
        else:
            return "You don't have a gotchi at the moment, you'll have to hatch one."


    def receive(self):
        try:
            response = requests.get(self.geturl, params=dict(offset=self.update_offset))
            return json.loads(response.text)

        except Exception:
            return dict(ok=False, description=Exception)


    def send(self, gotchi_id, message):
        requests.get(self.sendurl, params=dict(chat_id=gotchi_id, text=message))


def normalize(text):
    return  text.lstrip('/').lower()


### Logic ###

try:
    homedir = os.path.dirname(__file__)
    tokenfile = homedir + '/token'
    gotchifile = homedir + '/gotchis.save'
    
    token = ''
    with open(homedir + '/token', 'r') as f:
        token = f.readline().strip()

    gotchis = ''
    try:
        with open(gotchifile, 'rb') as f:
            gotchis = pickle.loads(f.read())

    except Exception:
        gotchis = dict()

    main = Main(token, gotchis)

    while True:
        main.tick()
        sleep(1)

except KeyboardInterrupt:
    with open(gotchifile, 'wb') as f:
        pickle.dump(gotchis, f)

    print("Exiting.")
    exit(0)

