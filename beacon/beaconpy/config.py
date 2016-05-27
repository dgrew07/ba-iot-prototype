# -*- coding: utf-8 -*-

"""
Configuration file.
"""

"""
Set the flags to determine were reports are stored/sent to and if visual feedback is given by the console.
At least one option should to be True.
"""
output_server = True
output_local = True
output_console = True

"""
Set ip address, port and API path for server receiving reports.
Set the absolute path where you want to store the local data.
The directories have to exist, they will not be created. You need writing permissions!
"""
server_addr = '192.168.1.2:3000'
server_apipath = '/api/beacon'
local_path_trips = '/home/beacon/data/trips'
local_path_temp = '/home/beacon/data/temp'

"""
Calibrate MPU-6050 accelerometer sensor output on startup.
Calculated offsets CAN be written to the MPU-6050 directly, but this feature should only be used once the sensor is properly installed.
"""
# calibrate_gps = False  << GPS calibration makes little to no sense right now. >>
calibrate_acc = True

"""
Refresh rates of the threads polling sensor data.
"""
tick_gpspoller = 0.1
tick_accpoller = 0.1

"""
Refresh rates of the threads building and sending/storing reports.
"""
tick_repbuilder = 1

"""
Refresh rate of the visualization thread (useful in development).
"""
tick_visualization = 0.5

"""
MPU-6050 accelerometer settings.
"""
acc_power_mgmt_1 = 0x6b
acc_power_mgmt_2 = 0x6c 
acc_bus = 2
acc_address = 0x68
acc_addr_x = 0x3b
acc_addr_y = 0x3d
acc_addr_z = 0x3f
acc_oneg = 9.80665 # 1G = 9,80665 m/s^2 (normal falling acceleration DIN 1305) or use 1G = 9,81 m/s^2 (in general)
acc_range = 4 # default range is +/- 2G