#! /usr/bin/python

import os
from gps import *
from time import *
import time
import threading
import random
import json
import Queue


# set global variables
sensors = None
gpsd = None 
accd = None
report = None
reportstr = 'noch kein Report'
queue = Queue.Queue()

# tick variables / refresh rate of threads
pollertick = 1
reportingtick = 2
dispatchingtick = 10

# clear terminal screen
os.system('clear') 


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class GpsPoller(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)
 
    self.running = True 
    self.tick = tick

    # bring gpsd into scope of thread
    global gpsd 

    # start stream of gps info
    gpsd = gps(mode=WATCH_ENABLE) 

  def run(self):
    global gpsd
    while self.running:
      #loop through gpsd data in order to clear the buffer and always write the latest data 
      gpsd.next() 
      
      # decode mode value
      if gpsd.fix.mode == 3:
        gpsd.fix.modeText = '3D'
      elif gpsd.fix.mode == 2:
        gpsd.fix.modeText = '2D'
      elif gpsd.fix.mode == 1:
        gpsd.fix.modeText = 'kein Fix'
      else:
        gpsd.fix.modeText = 'kein Wert'
        
      #time.sleep(self.tick) 
        

class AccPoller(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)
    
    self.running = True 
    self.tick = tick
    

    # bring accd into scope of thread
    global accd
    
    # init
    accd = Bunch(ax = 0, ay = 0, az = 0)


  def run(self):
    while self.running:
      # do stuff / read i2c stream
      
      # output scale for any setting is [-32768, +32767]
      # random dummy numbers
      a = -32768
      b = 32767
      local_random = random.Random()
      accd.ax = local_random.randint(a, b)
      accd.ay = local_random.randint(a, b)
      accd.az = local_random.randint(a, b)
      
      time.sleep(self.tick)   
      
class ReportingBuilder(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)

    self.running = True 
    self.tick = tick
    
    # bring accd into scope of thread
    global accd
    # bring gpsd into scope of thread
    global gpsd 
    # bring report into scope of thread and init
    global report
    global reportstr
    report = Bunch(time = 0, gpsfixtime = 0, gpslatitude = 0, gpslongitude = 0, gpsaltitude = 0, gpsspeed = 0, gpsmode = 0, gpssats = 0, accax = 0, accay = 0, accaz = 0)
    # bring queue into scope of thread
    global queue
    # bring sensor status into scope of thread
    global sensors

  def run(self):
    while self.running:
      # if sensor threads are running, write data to report and put it into queue
      if sensors == True:
        # timestamp
        report.time = gpsd.fix.time
        # gps data raw
        report.gpsfixtime = gpsd.fix.time
        report.gpslatitude = gpsd.fix.latitude
        report.gpslongitude = gpsd.fix.longitude
        report.gpsaltitude = gpsd.fix.altitude
        report.gpsspeed = gpsd.fix.speed
        report.gpsmode = gpsd.fix.modeText
        report.gpssats = len(gpsd.satellites)
        # acc data raw 
        report.accax = accd.ax
        report.accay = accd.ay
        report.accaz = accd.az
        # serialize report to json string
        reportstr = json.dumps(report.__dict__)
        
      time.sleep(self.tick)      

      
class ReportingDispatcher(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)

    self.running = True 
    self.tick = tick
    
    # bring accd into scope of thread
    global accd
    # bring gpsd into scope of thread
    global gpsd 
    # bring report into scope of thread
    global report
    # bring queue into scope of thread
    global queue

  def run(self):
    while self.running:
      # if queue is not empty -> aquire lock, build json string from reports in queue, send to server via http
      time.sleep(tick) 
      
if __name__ == '__main__':
  
  # create the thread for gps data
  gpsp = GpsPoller(pollertick) 
  # create the thread for acc data
  accp = AccPoller(pollertick) 
  # create the thread for building reports from sensor data
  repp = ReportingBuilder(reportingtick) 
  # create the thread for dispatching data to server
  disp = ReportingDispatcher(dispatchingtick) 
  
  try:
    # start all threads
    gpsp.start() 
    accp.start() 
    repp.start() 
    disp.start() 
    
    if gpsp.running == True and accp.running == True:
      sensors = True
    else:
      sensors = False
    
    while True:
      
      # clear python shell screen
      os.system('clear')
      
      print
      print ' Zeit aktuell (UTC)          ' , gpsd.utc
      print '----------------------------------------------------------------'
      print
      print ' GPS Daten (NL-302U)'
      print '----------------------------------------------------------------'
      print '   Zeit letzter Fix (UTC)    ' , gpsd.fix.time
      print '   geogr. Breite (DDD)       ' , gpsd.fix.latitude
      print '   geogr. Laenge (DDD)       ' , gpsd.fix.longitude
      print '   Hoehe (m)                 ' , gpsd.fix.altitude
      print '   Geschwindigkeit (m/s)     ' , gpsd.fix.speed
      print '   Modus                     ' , gpsd.fix.modeText
      print '   Anzahl Satelliten         ' , len(gpsd.satellites)
      print
      print ' Accelerometer Daten (MPU-6050)'
      print '----------------------------------------------------------------'
      print '   noch nicht implementiert, Dummy-Daten'
      print '   Beschleunigung X-Achse    ' , accd.ax
      print '   Beschleunigung Y-Achse    ' , accd.ay
      print '   Beschleunigung Z-Achse    ' , accd.az
      print 
      print '----------------------------------------------------------------'
      print ' Status Sensoren:            ' , sensors
      print ' Letzter Report:             ' , report.time
      print
      
      # refresh intervall
      time.sleep(1) 

  # kill threads with ctrl+c
  except (KeyboardInterrupt, SystemExit): 
    print "\nThreads werden beendet..."
    
    gpsp.running = False
    gpsp.join() 
    print "\nGPS Poller beendet!"
    
    accp.running = False
    accp.join() 
    print "Accelerometer Poller beendet!"
    
    sensors = False
    
    repp.running = False
    repp.join() 
    print "Reporter beendet!"
    
    repp.running = False
    repp.join() 
    print "Versender beendet!"
    
print "\nProgramm beendet."

  
  