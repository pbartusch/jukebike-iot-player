import spotify
import threading
import logging
from enum import Enum
import sys

from secret_config import SPOTIFY_AUTH

#TODO: Umgang mit Session Variablen verbessern?

logging.basicConfig(level=logging.WARNING)


class JukeTrack(spotify.Track):
    def __init__(self, session, track_uri):
        spotify.Track.__init__(self, session, uri=track_uri)
        self.votes = []


class JukeQueue:
    MAX_TRACKS_IN_QUEUE = 5
    MAX_TRACK_BY_SAME_USER = 999
    QUEUE_MODE = Enum('Mode', 'QUEUE_MODE VOTE_MODE')

    def getTrack(self, track_uri):
        return JukeTrack(self.session, track_uri).load()

    def __init__(self, session):
        #instance variables
        self.session = session
        self.queue = [self.getTrack('spotify:track:4iErBnl7V5FQZ1W7YJGyMT'), self.getTrack('spotify:track:4R3g0a8GUZg7EVKjH7QYmz'),
                     self.getTrack('spotify:track:5JtMPwbFUUQunFrwSq2nd9')]
        #  self.wishlist

    def pop(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return self.getTrack('spotify:track:5JtMPwbFUUQunFrwSq2nd9')

    def push(self, track_uri=None, track=None):
        assert track_uri or track
        if track_uri:
            track = self.getTrack(track_uri)
        self.queue.append(track)

    def vote(self, trackUri):
        pass


class SpotifyPlayer:
    def connection_state_listener(self, session, error_type):
        if error_type is spotify.ErrorType.OK and session.connection.state is spotify.ConnectionState.LOGGED_IN:
            print('Logged in as %s' % session.user)
            self.logged_in_event.set()
        else:
            print('Login failed: %s' % error_type)

    def track_state_listener(self, session):
        logging.debug("End of Track")
        self.next()

    def next(self):
        next_track = self.track_list.pop()
        print('Playing: %s' % next_track.name)
        self.session.player.load(next_track)
        self.session.player.play()
        self.status = self.Status.PLAYING
        self.current_track = next_track

    def add_track(self, track_uri):
        self.track_list.push(track_uri)
        print('added track')

    def play_track(self, track_uri):
        next_track = self.track_list.getTrack(track_uri)
        print('Playing: %s' % next_track.name)
        self.session.player.load(next_track)
        self.session.player.play()
        self.status = self.Status.PLAYING
        self.current_track = next_track

    def whats_playin(self):
        return self.current_track.name

    def play(self):
        #TODO: enum nutzen
        if self.session.player.state == "unloaded":
            self.next()
        else:
            self.session.player.play(1)

    def pause(self):
        self.session.player.play(0)

    def __init__(self):

        #instance variables
        self.logged_in_event = threading.Event()
        self.end_of_track_event = threading.Event()
        self.Status = Enum('Status', 'PAUSED PLAYING')
        self.status = self.Status.PAUSED

        # Login
        config = spotify.Config()
        keypath = sys.path[0]+"/spotify_appkey.key"
        config.load_application_key_file(filename=keypath)
        self.session = spotify.Session(config)
        self.session.login(SPOTIFY_AUTH['username'], SPOTIFY_AUTH['password'])

        # Define audio sink
        #audio = spotify.AlsaSink(self.session, "plughw:CARD=PCH")
        audio = spotify.AlsaSink(self.session)

        # Start Event Loop Thread, which automatically processes events from Lip
        event_loop = spotify.EventLoop(self.session)
        event_loop.start()

        # Register Listener for Login / End of Track / ...
        self.session.on(spotify.SessionEvent.LOGGED_IN, self.connection_state_listener)
        self.session.on(spotify.SessionEvent.END_OF_TRACK, self.track_state_listener) # is being called endlessly when track ends
        # to be implemented:
        #CONNECTION_ERROR
        #MESSAGE_TO_USER

        # Wait for Login to succeed
        self.logged_in_event.wait()

        # Initiate Queue
        self.track_list = JukeQueue(self.session)

        #self.next()

