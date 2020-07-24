# jukebike-iot-player
#saveThePlanetWithMusic JukeBike IOT player source code

# SET UP THE IOT (RASPBERRY PI)

## Hardware: audio setup

### Debug audio issues

Note: Test audio on pi using the following command:

```
speaker-test -c2 -twav -l7
```

Note: Install `alsa-utils` to debug sound issues:

```
sudo apt-get install alsa-utils
# list all sound devices
aplay -L
```

## Software: set up python environment

```
sudo pip3 install requests
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list
sudo apt-get update && sudo apt-get install -y libspotify-dev
sudo pip3 install pyspotify
sudo pip3 install pyalsaaudio
```

# DEVELOPMENT SETUP

Create `secret_config.py` with the following contents:

```
SPOTIFY_AUTH = {
    'username': '<spotify username>',
    'password': '<spotify password>'
}

JUKEBIKE_CONF = {
    'API_ROOT': '<URL to jukebike-cloud API>',
    'PCM_ID': '<PCM sound device ID>'
}
```

e.g., use this for hifiberry soundcard:

```
'PCM_ID': 'plughw:CARD=sndrpihifiberry,DEV=0'
```

# DEPLOY TO IOT

configure and run (on dev machine):

```
./deploy_jukebike_iot_player.sh
```

run (on IoT device / raspberry):

```
python3 jukebike_iot_player.py
```
