#/bin/bash

# TODO make configurable
export IOT_IP=192.168.177.32

ssh pi@$IOT_IP exec sudo rm -R /home/pi/jukebike-iot-player/
ssh pi@$IOT_IP exec mkdir /home/pi/jukebike-iot-player/
scp ./* ssh pi@$IOT_IP:/home/pi/jukebike-iot-player/
ssh pi@$IOT_IP exec sudo ps auxww | grep 'jukebike-iot-player' | awk '{print $2}' | xargs kill
#ssh pi@$IOT_IP exec sudo python3 /home/pi/jukebike-iot-player/jukebike_iot_player.py
