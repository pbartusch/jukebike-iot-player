# jukebike-iot-player
#saveThePlanetWithMusic JukeBike IOT player source code

# SET UP THE IOT (RASPBERRY PI)

## Hardware: Audio setup

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

## Hardware: Set up 4G connectivity

Plug USB LTE Stick onto RPi and install tooling:

```
sudo apt install wvdial
sudo apt install usb-modeswitch
```

Reboot.

Edit `/etc/wvdial.conf` - add a new `lte` section:
(adjusted solution from https://forum.siduction.org/index.php?topic=823.30)

```
[Dialer Defaults]
Init1 = ATZ # TODO removed!!!
Init2 = ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0 # TODO removed!!!
Modem Type = Analog Modem
ISDN = 0
New PPPD = yes
Modem = /dev/ttyUSB0
Baud = 921600 # maybe 9600, 57600, 115200 460800 or 760000

[Dialer pin]
Init3 = AT+CPIN=<SIM PIN>

[Dialer umts]
Carrier Check = no
Init4 = at+cgdcont=1,"IP","<ISP APN gateway>"
Stupid Mode = 1
Phone = *99#
Dialer Command = ATD
Dial Attemps = 2
Username = dontcare
Password = dontcare
```

Note: The following settings depend on your SIM & provider:

* Replace `<SIM PIN>`
* Replace `<ISP APN gateway>`

Test with:

```
sudo wvdial pin
sudo wvdial umts
```

Add LTE connect to boot routine:

Create `/lib/systemd/system/umts.service`:

```
[Unit]
Description=UMTS dial in
After=multi-user.target

[Service]
Type=idle
ExecStart=-/opt/wvdial_start.sh

[Install]
WantedBy=multi-user.target
```

```
sudo chmod 644 /lib/systemd/system/umts.service
sudo systemctl daemon-reload
sudo systemctl enable umts.service
sudo reboot
```

`/opt/wvdial_start.sh` (give `+x` permission):

```
#!/bin/bash

sleep 2
/usr/bin/wvdial pin
sleep 5
/usr/bin/wvdial umts

exit 0
```

Hint: Debug service using:

```
journalctl -u umts.service
```

## Software: Set up python environment (on RPi)

```
sudo pip3 install requests
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list
sudo apt-get update && sudo apt-get install -y libspotify-dev
sudo pip3 install pyspotify
sudo pip3 install pyalsaaudio
```

## Register jukebike-iot-player as service (on RPi)

Create `/lib/systemd/system/jukebike.service`:

```
[Unit]
Description=JukeBike IOT Player
Requires=multi-user.target

[Service]
Type=idle
#ExecStart=/usr/bin/python3 /home/pi/jukebike-iot-player/jukebike_iot_player.py
ExecStart=/bin/bash /home/pi/jukebike-iot-player/start_service.sh

[Install]
WantedBy=multi-user.target
```

```
sudo chmod 644 /lib/systemd/system/jukebike.service
sudo systemctl daemon-reload
sudo systemctl enable jukebike.service
sudo reboot
```

Hint: Debug service using:

```
journalctl -u jukebike.service
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
