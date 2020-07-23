import logging
from player import SpotifyPlayer
from controller import JukeController

# config logger

logging.basicConfig(level=logging.DEBUG)

# init the player and start the controller

controller = JukeController()
with_player = SpotifyPlayer(controller)

controller.start(with_player)
