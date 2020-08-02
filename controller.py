import sys
import subprocess
import requests
import json
import time
import logging
import threading
from secret_config import JUKEBIKE_CONF

logger = logging.getLogger()

API_ROOT = JUKEBIKE_CONF['API_ROOT']
CALL_WHATS_NEXT = '/whats-next'
CALL_IOT_SETTINGS = '/iot-settings'

class JukeController:

    def play_next(self, played_id = None):
        whats_next_prm = ""
        # TODO distinguish between pure GET vs PUT when accessing with "playedTrack"
        if played_id != None:
            whats_next_prm = "trackPlayed={}".format(played_id)
        res_whats_next = requests.get('{}{}?{}'.format(API_ROOT, CALL_WHATS_NEXT, whats_next_prm))
        logger.debug('res_whats_next.status_code = {}'.format(res_whats_next.status_code))

        if (res_whats_next.status_code == 200):
            new_playlist = res_whats_next.json()
            logger.debug('new_playlist = {}'.format(json.dumps(new_playlist)))
            if(len(new_playlist) > 0):
                self._player.play_track(new_playlist[0])
            else:
                logger.warn('play_next: no next song to play ... sleeping 5 sec, and requery cloud!')
                time.sleep(5)
                self.play_next(played_id)
        else:
            logger.warn('res_whats_next got status_code = {} from API'.format(res_whats_next.status_code))

    def notify_track_ended(self, played_id):
        logger.info('In notify_track_ended')
        logger.info(':: played_id = {}'.format(played_id))
        self.play_next(played_id)

    def load_iot_settings(self):
        try:
            res_settings = requests.get('{}{}'.format(API_ROOT, CALL_IOT_SETTINGS))
            if (res_settings.status_code == 200):
                settings = res_settings.json()
                if ((self.last_settings is None) | (json.dumps(self.last_settings, sort_keys=True) != json.dumps(settings, sort_keys=True))):
                    # set volume using amixer (from OS)
                    logger.info('load_iot_settings :: set volume to {}'.format(settings.volume))
                    subprocess.call(["amixer", "set PCM {}%".format(settings.volume)])
                else:
                    logger.debug('load_iot_settings :: nothing to do!')
            else:
                logger.warn('load_iot_settings :: res_settings.status_code does not equal 200')
        except:
            e = sys.exc_info()[0]
            logger.warn('exception in load_iot_settings :: e = {}'.format(e))

    def event_loop(self):
        self.play_next()
        while True:
            self.load_iot_settings()
            time.sleep(5)

    def start(self, with_player):
        self._player = with_player
        self.last_settings = None
        self.event_loop()
