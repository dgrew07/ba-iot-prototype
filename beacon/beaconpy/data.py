# -*- coding: utf-8 -*-
# data.py

import Queue

"""
Initialise data dictionaries in order to share information between threads.
"""

gps_dict = dict.fromkeys(['fixtime','latitude','longitude','altitude','speed','mode','satellites'])   
acc_dict = dict.fromkeys(['axis_x','axis_y','axis_z'])
report_dict = dict.fromkeys(['counter','time','gps_fixtime','gps_latitude','gps_longitude','gps_altitude','gps_speed','gps_mode','gps_satellites','acc_axis_x','acc_axis_y','acc_axis_z'])
trip_dict = dict.fromkeys(['time_start','time_end','info','reports']) 
report_queue = Queue.Queue() # inits a FIFO queue