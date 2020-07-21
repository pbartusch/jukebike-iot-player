import spotify
import threading
import logging
import time
import sys

from secret_config import SPOTIFY_AUTH

# pip install pyspotify
# sudo apt-get install libasound2-dev
# pip install pyalsaaudio

logging.basicConfig(level=logging.WARNING)
logged_in_event = threading.Event()
end_of_track_event = threading.Event()
tracklist = []


def connection_state_listener(session, error_type):
    if error_type is spotify.ErrorType.OK and session.connection.state is spotify.ConnectionState.LOGGED_IN:
        print('Logged in as %s' % session.user)
        logged_in_event.set()
    else:
        print('Login failed: %s' % error_type)


def track_state_listener(session):
    print("End of Track")
    end_of_track_event.set()

def play_next_track(track_uri):
    track = session.get_track(track_uri).load()
    print('Playing: %s' % track.name)
    session.player.load(track)
    session.player.play()

def add_track(track_uri):
    tracklist.append('spotify:track:5JtMPwbFUUQunFrwSq2nd9')
    print('added track')

def startme():
    # Login
    config = spotify.Config()
    keypath = sys.path[0] + "/spotify_appkey.key"
    config.load_application_key_file(filename=keypath)
    session = spotify.Session(config)
    session.login(SPOTIFY_AUTH['username'], SPOTIFY_AUTH['password'])

    # Define audio sink
    audio = spotify.AlsaSink(session)

    # Start Event Loop Thread, which automatically processes events from Lip
    event_loop = spotify.EventLoop(session)
    event_loop.start()

    # Register Listener for Login / End of Track / ...
    session.on(spotify.SessionEvent.LOGGED_IN, connection_state_listener)
    session.on(spotify.SessionEvent.END_OF_TRACK, track_state_listener) # is being called endlessly after track ends
    # to be implemented:
    #CONNECTION_ERROR
    #MESSAGE_TO_USER

    # Wait for Login to succeed
    logged_in_event.wait()

    # Loop Playlist
    tracklist = ['spotify:track:4iErBnl7V5FQZ1W7YJGyMT', 'spotify:track:4R3g0a8GUZg7EVKjH7QYmz', 'spotify:track:5JtMPwbFUUQunFrwSq2nd9']
    for track in tracklist:
        end_of_track_event.clear()
        play_next_track(track)
        end_of_track_event.wait()
