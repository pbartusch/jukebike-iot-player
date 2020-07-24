import spotify
import threading
import logging
import sys
from secret_config import SPOTIFY_AUTH, JUKEBIKE_CONF

logger = logging.getLogger()
#logging.getLogger('spotify').setLevel(logging.DEBUG)
logging.getLogger('spotify').setLevel(logging.INFO)

class SpotifyPlayer:

    def connection_state_listener(self, session, error_type):
        if error_type is spotify.ErrorType.OK and session.connection.state is spotify.ConnectionState.LOGGED_IN:
            logger.debug('In connection_state_listener :: session.user = {}'.format(session.user))
            self.logged_in_event.set()
        else:
            logger.error('In connection_state_listener :: login failed: error_type = '.format(error_type))

    def track_state_listener(self, session):
        if self.end_of_track_event.is_set():
            logger.debug("track_state_listener already called ... returning!")
            return
        else:
            logger.debug("In track_state_listener (without conflicting call)")
            self.end_of_track_event.set()
            self.is_playing = False
            self._controller.notify_track_ended(self.current_track_uri)

    def play_track(self, track_uri):
        next_track = spotify.Track(self.session, uri=track_uri).load()
        logger.debug('In play_track :: next_track.name = {}'.format(next_track.name))
        self.session.player.load(next_track)
        self.session.player.play()
        self.current_track = next_track
        self.current_track_uri = track_uri
        self.is_playing = True
        self.end_of_track_event.clear()

    def get_current_track(self):
        return self.current_track.name

    # TODO consider encapsulation of controller as observer/notification pattern
    def __init__(self, controller):

        self._controller = controller
        self.current_track = None
        self.current_track_uri = None
        self.is_playing = False

        # spotify player instance variables
        self.logged_in_event = threading.Event()
        self.end_of_track_event = threading.Event()

        # spotify API config & login
        config = spotify.Config()
        keypath = sys.path[0]+"/spotify_appkey.key"
        config.load_application_key_file(filename=keypath)
        self.session = spotify.Session(config)
        self.session.login(SPOTIFY_AUTH['username'], SPOTIFY_AUTH['password'])

        # define audio sink
        spotify.AlsaSink(self.session, JUKEBIKE_CONF['PCM_ID'])

        # start event loop thread, which automatically processes events from lip
        event_loop = spotify.EventLoop(self.session)
        event_loop.start()

        # register listener for login, end of track / ...
        self.session.on(spotify.SessionEvent.LOGGED_IN, self.connection_state_listener)
        self.session.on(spotify.SessionEvent.END_OF_TRACK, self.track_state_listener) # is being called endlessly when track ends
        # TODO to be implemented, if necessary
        #CONNECTION_ERROR
        #MESSAGE_TO_USER

        # wait for login to succeed
        self.logged_in_event.wait()
