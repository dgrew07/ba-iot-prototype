# Prototypical Development of a System for the Analysis of Driving Behaviour for Motor Vehicles
## The beacon - reading and transmitting sensor data

### Getting started
The program is built around the MPU-6050 accelerometer & gyroscope sensor and the Navilock NL-302U GPS dongle, but any GPS device which is supported by the python gpsd daemon will do. Please refer to http://catb.org/gpsd/ in order to see if your device and operating system is supported.

#### Installing required software and packages
The beacon was developed for Bananian Linux, an optimised version of Debian 8 for Banana Pi/Pro. Below a brief instruction will show you how to install and configure the required software and hardware with the apt package manager.
##### Install and run gpsd GPS daemon
- use `sudo apt-get install gpsd gpsd-clients`
- connect a supported USB GPS dongle to a linux platform
- use `lsusb` to see if the GPS dongle was recognised
- use `dmesg` to find the mounting path of the dongle, e.g. `/dev/ttyUSB0`
- run gpsd with `gpsd -n /dev/ttyUSB0`, which will force gpsd to always to read data from the dongle even if no application requesting GPS positions is running
- run `cgps` or `gpsmon` to see if the dongle is transmitting data
Please refer to the gpsd ddocumentation for further information: http://www.catb.org/gpsd/#documentation

##### Connect the MPU-6050 sensor
- use the Fritzing-sketch in `beacon/docs` to see how the sensor needs to be wired to a Banana Pi M1
- see list of i2c-busses the MPU-6050 could be running on: `ls -l /dev/i2c*`
- use `i2cdetect -y <bus-nr>` e.g. `i2cdetect -y 1`, the default MPU-6050 address should be `0x68` 
- install `sudo apt-get install build-essential libi2c-dev i2c-tools python-dev` and reboot
- you are now ready to read the data output of the MPU-6050 with the beacon

#### Configure and start the beacon
- configure the config.py file in `beacon/beaconpy` depending on your preferences
- right now the program is not installable, just run the main.py script with the CPython Interpreter (prefered) in `beacon/beaconpy`: `python /<path.to.beacon>/beacon/beaconpy/main.py`
- you will need writing privileges in the correspondig directory, or the program will throw an exception
