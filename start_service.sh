#/bin/bash

INTERNET_STATUS=false
while [ "$INTERNET_STATUS" = false ]
do
  ping -c 1 -W 0.7 8.8.4.4 > /dev/null 2>&1
  if [ $? -eq 0 ] ; then
    echo "Internet present"
    INTERNET_STATUS=true
  else
    echo "Internet DOWN"
    INTERNET_STATUS=false

    # TODO nasty hack!
    PPP0_IP=`ip route | grep "dev ppp0 proto kernel scope link src" | awk '{print $1}'`
    if [ -z "$PPP0_IP" ] ; then
      echo "No ppp0 device found"
    else
      route add default gw $PPP0_IP ppp0
    fi

  fi

  sleep 1
done;

# TODO
python3 /home/pi/jukebike-iot-player/jukebike_iot_player.py
