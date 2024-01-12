from flask import Flask, Response
import requests
import json
import urllib.parse
from os import path
import datetime
import os
import time
import logging

from helpers import log, DEBUG

class PROXY():
    
    def __init__(self, jambox, channels, host, port, threaded, cookie, debug):
        self.jambox = jambox
        self.token = ''
        self.user  = ''
        self.channels = channels
        self.cookie = cookie

        self.app = Flask('Jambox Go decoder')
        logger = logging.getLogger('werkzeug')
        logger.setLevel(logging.ERROR)

        self.app.route("/<id>")(self.channel)
        self.app.run(host=host, port=port, threaded=threaded)


    def req(self, url):
        r = requests.get(url=url)
        if(r.status_code == 404):
            for i in range(200):
                time.sleep(0.005)
                r = requests.get(url=url)
                if(r.status_code == 200):
                    log(DEBUG, '404 retires {}'.format(i))
                    break

        if(r.status_code == 403):
            query = self.jambox.getToken().decode().split('"')[3]
            self.token = urllib.parse.quote(query, safe='')
            self.token = self.token.replace('%5C', '')
            self.user = self.cookie.get('id')
            self.user = self.user.strip('\\')
            self.user = urllib.parse.quote(self.user, safe='')
            log(DEBUG, 'New token: {} user: {}'.format(self.token[0:10] + '************', self.user[0:10] + '************'))
        return r


    def channel(self, id):
        log(DEBUG, 'CHANNEL: {}'.format(self.channels[int(id)][0]))

        my_str = self.channels[int(id)][1]
        idx = my_str.index('playlist.m3u8')
        my_str = my_str[:idx] + 'high/' + my_str[idx:]
        
        log(DEBUG, 'Reqest url: {}'.format(my_str))

        url = '{}?token={}&hash={}'.format(my_str, self.token, self.user)
        
        r = self.req(url)

        if(r.status_code != 200):
            url = '{}?token={}&hash={}'.format(my_str, self.token, self.user)
            r = self.req(url)
        
        file = r.content.decode().split('\n')
        key = file[2].split('URI="')[1]
        channel_url = file[6].split('/hls_scr_aac')[0]

        file[2] = '#EXT-X-KEY:METHOD=AES-128,URI="'+channel_url+key

        index1 = file[6].find('playlist')
        index2 = file[6].find('.', index1)

        chunk = int(file[6][index1+8:index2])
        log(DEBUG, 'Playing chunks: {}, {}, {}'.format(chunk-1, chunk, chunk+1))

        file[6].replace('playlist{}'.format(chunk), 'playlist{}'.format(chunk-1))
        file[8].replace('playlist{}'.format(chunk+1), 'playlist{}'.format(chunk))
        file[10].replace('playlist{}'.format(chunk+2), 'playlist{}'.format(chunk+1))

        out = ""
        for line in file:
            out = out + line + "\n"

        return Response(out, mimetype='text/plain', headers={'Content-disposition': 'attachment; filename=playlist.m3u8'})