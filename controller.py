import requests
import json
import time
import logging
from secret_config import JUKEBIKE_CONF

logger = logging.getLogger()

CALL_WHATS_NEXT = 'whatsnext'

class JukeController:

    def notify_track_ended(self):
        logger.info('In notify_track_ended')

    def event_loop(self):
        API_ROOT = JUKEBIKE_CONF['API_ROOT']

        while True:
            res_whats_next = requests.get('{}/{}'.format(API_ROOT, CALL_WHATS_NEXT))
            logger.debug('res_whats_next.status_code = {}'.format(res_whats_next.status_code))

            if (not self._player.is_playing):
                if (res_whats_next.status_code == 200):
                    new_playlist = res_whats_next.json()
                    logger.debug('new_playlist = {}'.format(json.dumps(new_playlist)))
                    # TODO songs from API dont work so far? ... but this hard coded song does!
                    #self._player.play_track(new_playlist[0])
                    self._player.play_track('spotify:track:4afIDYk3UUZOSuPEot4tL1')
                else:
                    logger.warn('res_whats_next got status_code = {} from API'.format(res_whats_next.status_code))

            time.sleep(1)

    def start(self, with_player):
        self._player = with_player
        self.event_loop()
