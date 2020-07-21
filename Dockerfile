FROM python:3

#sudo docker build -t spotifyproject .
#sudo docker run -p 80:5000 --device /dev/snd -it spotifyproject

# Debugging sound issues
# install alsa-utils: apt-get install alsa-utils
#  list devices: aplay -L
# test different devices, e.g. speaker-test plughw:CARD=PCH
# if it works => change audio sink:  audio = spotify.AlsaSink(self.session, "plughw:CARD=PCH")

ADD main.py spotifyPlayer.py swagger.yml spotify_appkey.key /

RUN apt-get update && apt-get install -y --force-yes wget gnupg

RUN wget -q -O - https://apt.mopidy.com/mopidy.gpg | apt-key add -

RUN wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

RUN apt-get update && apt-get install -y --force-yes libasound2-dev python3-pip libspotify-dev python-spotify

RUN pip3 install flask connexion swagger-ui-bundle pyalsaaudio pyspotify

CMD [ "python3", "./main.py" ]
