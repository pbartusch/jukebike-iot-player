import requests
import json
import time
import logging
import threading
from secret_config import JUKEBIKE_CONF

logger = logging.getLogger()

API_ROOT = JUKEBIKE_CONF['API_ROOT']
CALL_WHATS_NEXT = '/whats-next'

class JukeController:

    def play_next(self, played_id = None):
        whats_next_prm = ""
        # TODO distinguish between pure GET vs PUT when accessing with "playedTrack"
        if played_id != None:
            whats_next_prm = "?trackPlayed={}".format(played_id)
        res_whats_next = requests.get('{}{}{}'.format(API_ROOT, CALL_WHATS_NEXT, whats_next_prm))
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

    def event_loop(self):
        self.play_next()
        while True:
            time.sleep(10)

    def start(self, with_player):
        self._player = with_player
        self.event_loop()
