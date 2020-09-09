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
CALL_IOT_SETTINGS = '/status'

class JukeController:

    def log_sys_exc(self, in_routine):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.warn('Exception in {}'.format(in_routine))
        logger.warn(':: exc_type = {}'.format(exc_type))
        logger.warn(':: exc_value = {}'.format(exc_value))
        logger.warn(':: exc_traceback = {}'.format(exc_traceback))

    def play_next(self, played_id = None):
        whats_next_prm = ""
        if played_id != None:
            whats_next_prm = "trackPlayed={}".format(played_id)

        try:
            # TODO distinguish between pure GET vs PUT when accessing with "playedTrack"
            res_whats_next = requests.get('{}{}?{}'.format(API_ROOT, CALL_WHATS_NEXT, whats_next_prm))
            logger.debug('res_whats_next.status_code = {}'.format(res_whats_next.status_code))

            if (res_whats_next.status_code == 200):
                new_playlist = res_whats_next.json()
                logger.debug('new_playlist = {}'.format(json.dumps(new_playlist)))
                if(len(new_playlist) > 0):
                    self._player.play_track(new_playlist[0])
                else:
                    logger.info('play_next: no next song to play ... will requery the cloud in 5 sec!')
                    time.sleep(5)
                    self.play_next(played_id)
            else:
                logger.warn('res_whats_next got status_code = {} from API'.format(res_whats_next.status_code))
        except:
            self.log_sys_exc('play_next')
            logger.warn('play_next failed for an unknown exception (maybe the connection got lost) ... retrying in 5 sec!')
            time.sleep(5)
            self.play_next(played_id)

    def notify_track_ended(self, played_id):
        logger.info('In notify_track_ended :: played_id = {}'.format(played_id))
        self.play_next(played_id)

    def load_iot_settings(self):
        try:
            res_settings = requests.get('{}{}'.format(API_ROOT, CALL_IOT_SETTINGS))
            if (res_settings.status_code == 200):
                logger.debug("load_iot_settings :: got 200")
                settings = res_settings.json()
                logger.debug(":: settings = {}".format(json.dumps(settings)))
                logger.debug(":: self.last_settings = {}".format(self.last_settings))
                # TODO refactor!!!
                b_set_volume = False
                if (self.last_settings is None):
                    logger.debug(":: self.last_settings is None")
                    b_set_volume = True
                else:
                    logger.debug(":: self.last_settings is NOT None")
                    if json.dumps(self.last_settings, sort_keys=True) != json.dumps(settings, sort_keys=True):
                        logger.debug(":: change in self.last_settings")
                        b_set_volume = True
                    else:
                        logger.debug(":: NO change in self.last_settings")
                if b_set_volume:
                    # set volume using amixer (from OS)
                    logger.info('load_iot_settings :: set volume to {}'.format(settings['volume']))
                    # TODO make adressing the sound card configurable or - even better - inferr from current JUKEBIKE_CONF
                    subprocess.call(["amixer", "-c", "1", "set", "Digital", "{}%".format(settings['volume'])])
                    self.last_settings = settings
                else:
                    logger.debug('load_iot_settings :: nothing to do!')
            else:
                logger.warn('load_iot_settings :: res_settings.status_code does not equal 200')
        except:
            self.log_sys_exc('load_iot_settings')

    def event_loop(self):
        self.play_next()
        while True:
            self.load_iot_settings()
            time.sleep(5)

    def start(self, with_player):
        self._player = with_player
        self.last_settings = None
        self.event_loop()
