import helpers
import json

from api import API
from proxy import PROXY

helpers.disableWinConSole()

if helpers.checkFiles():
    with open(helpers.files[0], 'r') as openfile:
        CONFIG = json.loads(json.load(openfile))
        helpers.debug = CONFIG['debug']
    
    with open(helpers.files[1], 'r') as openfile:
        CREDENTIALS = json.loads(json.load(openfile))

    try:
        with open(helpers.files[2], 'r') as openfile:
            COOKIES = json.loads(json.load(openfile))
    except:
            COOKIES = ''

    jambox = API(CREDENTIALS, COOKIES)

    if(helpers.checkChannels()):
        helpers.exportChannels(jambox, CONFIG['hls'])
    
    if(helpers.checkList()):
        helpers.exportList(CONFIG['host'], CONFIG['port'])

    with open(helpers.channelsFile, 'r') as openfile:
        channels = json.loads(openfile.read())

    with open(helpers.files[2], 'r') as openfile:
        COOKIES = json.loads(json.load(openfile))

    PROXY(jambox, channels, CONFIG['host'], CONFIG['port'], CONFIG['threaded'], COOKIES, CONFIG['debug'])
