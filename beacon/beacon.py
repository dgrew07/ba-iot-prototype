#! /usr/bin/python

import os
from gps import *
from time import *
import time
import threading
import Queue

#set global variables
gpsd = None 
gyrod = None
queue = Queue.Queue()

# clear terminal screen
os.system('clear') 

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)

    # bring gpsd into scope
    global gpsd 

    # start stream of gps info
    gpsd = gps(mode=WATCH_ENABLE) 
    self.current_value = None

    # set the running thread to true
    self.running = True 

  def run(self):
    global gpsd
    while gpsp.running:
      #loop through gpsd data in order to clear the buffer and alway get the latest data and grab EACH set of gpsd info to clear the buffer
      gpsd.next() 

if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
	  
      report = None
      report.time = None
      report.gps = None
      
      # clear python shell screen
      os.system('clear')
      
      # decode mode value
      if gpsd.fix.mode == 3:
        modeText = '3D'
      elif gpsd.fix.mode == 2:
        modeText = '2D'
      elif gpsd.fix.mode == 1:
        modeText = 'kein Fix'
      else:
        modeText = 'kein Wert'

      print
      print ' Zeit (UTC)                ' , gpsd.utc
      print '----------------------------------------------------------------'
      print
      
      print ' GPS Daten'
      print '----------------------------------------------------------------'
      print ' geogr. Breite (DDD)       ' , gpsd.fix.latitude
      print ' geogr. Laenge (DDD)       ' , gpsd.fix.longitude
      print ' Hoehe (m)                 ' , gpsd.fix.altitude
      print ' Geschwindigkeit (m/s)     ' , gpsd.fix.speed
      print ' Modus                     ' , modeText
      print
      print ' Gyroskop Daten'
      print '----------------------------------------------------------------'
      print ' noch nicht implementiert'
      print
      
      report.time = gpsd.utc
      report.gps.latitude = gpsd.fix.latitude
      report.gps.longtude = gpsd.fix.longtude
      report.gps.altitude = gpsd.fix.altitude
      report.gps.speed = gpsd.fix.speed
      report.gps.mode = modeText

      time.sleep(1) # refresh intervall

  # kill thread with ctrl+c
  except (KeyboardInterrupt, SystemExit): 
    print "\nThread wird beendet..."
    gpsp.running = False
    # wait for thread to finish actions
    gpsp.join() 
print "\nBeendet."