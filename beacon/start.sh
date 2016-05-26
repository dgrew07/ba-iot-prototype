#!/bin/bash

# kill gpsd processes
killall gpsd
sleep 1

# start gpsd with device and 'always calculate fix'-option
gpsd -n /dev/ttyUSB0
sleep 5

# start python script
python /home/beacon/beaconpy/main.py 





