import requests
import math
import time
import json
import random
import string
import hmac
import hashlib
import base64
import os
from os import path
import helpers


class API:
    def __init__(self, CREDENTIALS, COOKIE):

        self.COOKIE = COOKIE
        self.CREDENTIALS = CREDENTIALS

        self.DEVICE = 'other'

        self.API_URL = 'https://api.sgtsa.pl/'

        if COOKIE == '':
            self.login()

        with open(helpers.files[2], 'r') as openfile:
            jr = json.loads(json.load(openfile))
            self.ID = jr.get('id')
            self.SEED = jr.get('seed')
            self.IMPERSONATE = jr.get('devices')[0].get('id')


    def getAuthHeaders(self, data):
        return {
                "host": 'api.sgtsa.pl',
                "Accept": '*/*',
                "X-Auth": data[1],
                "X-Nonce": data[0],
                "sec-ch-ua": 'Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                "X-Device-Id": self.ID,
                "X-Device-Type": self.DEVICE,
                "X-Impersonate": self.IMPERSONATE,
                "Sec-Fetch-Dest": 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': 'Windows'
            }


    def randomString(self, length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


    def getTime30(self):
        return str(math.floor(time.time()/30)*30)


    def auth(self, endpoint):
        nonce = self.randomString(36)[2:13] + self.randomString(36)[2:13]
        date = self.getTime30()

        signature = hmac.new(
            self.SEED.encode(),
            (nonce + endpoint + date).encode(),
            hashlib.sha256
        ).hexdigest()

        return (nonce, base64.b64encode(signature.encode("utf-8")))


    def login(self):
        ENDPOINT = 'v1/auth/login'
        url = self.API_URL + ENDPOINT

        headers = {'host': 'api.sgtsa.pl', 'X-Time': self.getTime30()}

        response = requests.post(url, headers=headers, json=self.CREDENTIALS)
        helpers.log(helpers.DEBUG, 'Login status: {}'.format(response.status_code))

        
        with open(helpers.files[2], "w") as outfile:
            outfile.write(json.dumps(response.text, indent=4))


    def getToken(self):
        ENDPOINT = 'v1/ott/token'
        url = self.API_URL + ENDPOINT

        headers = self.getAuthHeaders(self.auth(ENDPOINT))

        response = requests.get(url=url, headers=headers)
        helpers.log(helpers.DEBUG, 'Token status: {}'.format(response.status_code))
        return response.content


    def setChannel(self, endpointID):
        ENDPOINT = 'v1/ott/dash/{}'.format(endpointID)
        url = self.API_URL + ENDPOINT

        headers = self.getAuthHeaders(self.auth(ENDPOINT))

        response = requests.get(url=url, headers=headers)
        helpers.log(helpers.DEBUG, 'Set channel status: {}'.format(response.status_code))


    def getLicense(self, endpointID, data):
        ENDPOINT = 'v1/ott/dash/{}/widevine/'.format(endpointID)
        url = self.API_URL + ENDPOINT

        headers = self.getAuthHeaders(self.auth(ENDPOINT))

        response = requests.post(url, headers=headers, data=data)
        helpers.log(helpers.DEBUG, 'License status: {}'.format(response.status_code))

        return response


    def getAsset(self):
        ENDPOINT = 'v1/asset'
        url = self.API_URL + ENDPOINT

        headers = self.getAuthHeaders(self.auth(ENDPOINT))
        response = requests.get(url, headers=headers)

        return response


    def getChannel(self, endpointID):
        ENDPOINT = 'v1/ott/dash/{}'.format(endpointID)
        url = self.API_URL + ENDPOINT

        headers = self.getAuthHeaders(self.auth(ENDPOINT))
        response = requests.get(url, headers=headers)

        return response
