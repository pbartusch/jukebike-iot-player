import connexion
import spotifyPlayer


player = None

print("neu gestartet")

def status():
    init_player()
    return player.whats_playin()


def next_track():
    init_player()
    player.next()


def play():
    init_player()
    player.play()


def pause():
    init_player()
    player.pause()


def add_track(track_uri):
    init_player()
    player.add_track(track_uri)


def play_track(track_uri):
    init_player()
    player.play_track(track_uri)


def init_player():
    #TODO: Eleganter zu lösen über x-swagger-router-controller?
    global player
    if player is None:
        print("Initiating Player")
        player = spotifyPlayer.SpotifyPlayer()


# Create the application instance
app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

