#! /usr/bin/python

import os
from gps import *
from time import *
import time
import datetime
import threading
import json
import glob
import smbus
import math
import httplib
import urllib
import Queue

# set global variables !! ENCAPSULATE THIS INTO A CLASS !!
sensors = None
gpsd = None 
accd = None
report = None
queue = Queue.Queue()

# tick variables / refresh rate of threads !! ENCAPSULATE THIS INTO A CLASS OR CONFIG FILE !!
pollertick = 0.1
reportingtick = 2
dispatchingtick = 40
displaytick = 0.1

# clear terminal screen
os.system('clear') 

def main():

  global gpsd
  global accd
  global report
  global queue

  # spawn threads
  gpsp = GpsPoller(pollertick) 
  accp = AccPoller(pollertick) 
  repp = ReportingBuilder(reportingtick) 
  disp = ReportingDispatcher(dispatchingtick) 
  
  try:
    # start all threads
    gpsp.start() 
    accp.start() 
    print
    print ' Starte Sensoren, bitte warten ...'
    time.sleep(3)
    repp.start() 
    disp.start() 
    
    while True:
      
      # clear python shell screen
      os.system('clear')
      
      print
      print ' Zeit aktuell (UTC)            ' , ToIso(UtcNow())
      print '----------------------------------------------------------------'
      print
      print ' GPS Daten (NL-302U)'
      print '----------------------------------------------------------------'
      print '   Zeit letzter Fix (UTC)      ' , gpsd.fix.time
      print '   geogr. Breite (DDD)         ' , gpsd.fix.latitude
      print '   geogr. Laenge (DDD)         ' , gpsd.fix.longitude
      print '   Hoehe (m)                   ' , gpsd.fix.altitude
      print '   Geschwindigkeit (m/s)       ' , gpsd.fix.speed
      print '   Modus                       ' , gpsd.fix.modeText
      print '   Anzahl Satelliten           ' , len(gpsd.satellites)
      print
      print ' Accelerometer Daten (MPU-6050)'
      print '----------------------------------------------------------------'
      print '   Beschl. X-Achse (m/s^2)     ' , accd.ax
      print '   Beschl. Y-Achse (m/s^2)     ' , accd.ay
      print '   Beschl. Z-Achse (m/s^2)     ' , accd.az
      print 
      print '----------------------------------------------------------------'
      print ' Letzter Report:               ' , report.time
      print ' Reports in Warteschlange:     ' , queue.qsize()
      
      # refresh intervall
      time.sleep(displaytick) 

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
  threading.enumerate()
  os._exit(1)

def ToIso(date):
  try:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(date)))
  except:
    return date

def UtcNow():
    now = datetime.datetime.utcnow()
    return (now - datetime.datetime(1970, 1, 1)).total_seconds()

class Bunch:
  def __init__(self, **kwds):
    self.__dict__.update(kwds)
  def to_JSON(self):
    return json.dumps(self, default = lambda o: o.__dict__, 
      sort_keys = False, indent = 4)

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
      
      try:
        # decode mode value
        if gpsd.fix.mode == 3:
          gpsd.fix.modeText = '3D'
        elif gpsd.fix.mode == 2:
          gpsd.fix.modeText = '2D'
        elif gpsd.fix.mode == 1:
          gpsd.fix.modeText = 'kein Fix'
        else:
          gpsd.fix.modeText = 'kein Wert'
          
        gpsd.fix.time = ToIso(gpsd.fix.time)
      
      except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
      
class AccPoller(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)
    
    self.running = True 
    self.tick = tick

    self.power_mgmt_1 = 0x6b
    self.power_mgmt_2 = 0x6c
    self.bus = smbus.SMBus(2) # this is the i2d-device number e.g. /dev/i2c-2
    self.address = 0x68       # this is the address value read via the i2cdetect command

    # bring accd into scope of thread
    global accd
    
    # init
    accd = Bunch(ax = 0, ay = 0, az = 0)
    self.bus.write_byte_data(self.address, self.power_mgmt_1, 0) # wake mpu 6050 from sleep mode (default)

  def read_word(self, adr):
    high = self.bus.read_byte_data(self.address, adr)
    low = self.bus.read_byte_data(self.address, adr+1)
    val = (high << 8) + low
    return val

  def read_word2c(self, adr):
    val = self.read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

  def run(self):
    while self.running:
      # read data
      accel_xout = self.read_word2c(0x3b)
      accel_yout = self.read_word2c(0x3d)
      accel_zout = self.read_word2c(0x3f)

      # scale data and calculate m/s^2
      # default range is 2G (2^14 = 16384)
      # g = 9,81 m/s^2 (in general)
      # g = 9,80665 m/s^2 (normal falling acceleration DIN 1305)
      # e.g. 9,81 / 16384 = 0,00059875
      scale_din = 9.80665 / 16384
      scale_gen = 9.81 / 16384
      accd.ax = accel_xout * scale_din
      accd.ay = accel_yout * scale_din
      accd.az = accel_zout * scale_din
      
      time.sleep(self.tick)   
      
class ReportingBuilder(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)

    self.running = True 
    self.tick = tick
    self.counter = 0
    
    global accd
    global gpsd 
    global report
    report = Bunch(counter = 0, time = 0, gpsfixtime = 0, gpslatitude = 0, gpslongitude = 0, gpsaltitude = 0, gpsspeed = 0, gpsmode = 0, gpssats = 0, accax = 0, accay = 0, accaz = 0)
    global queue
    
  def run(self):
    while self.running:

      time.sleep(self.tick)  

      # if sensor threads are running, write data to report and put it into queue
      # todo

      # report-id / counter
      self.counter += 1 
      report.counter = self.counter
      # timestamp
      report.time = ToIso(UtcNow())
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
      # todo: check if report holds usable data

      queue.put(report.to_JSON())
        
class ReportingDispatcher(threading.Thread):
  def __init__(self, tick):
    threading.Thread.__init__(self)

    self.running = True 
    self.tick = tick
    
    # bring queue into scope of thread
    global queue

  def run(self):
    while self.running:
    
      time.sleep(self.tick)
      
      packagelist = []
      while queue.empty() == False:
        packagelist.append(queue.get())
        queue.task_done()

      filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
      with open(filename + '.json', 'w') as outfile:
        json.dump(packagelist, outfile)
      
      #try:
      #  params = urllib.urlencode(json.dumps(packagelist)
      #  #headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
      #  connection = httplib.HTTPConnection('server.url:8000')
      #  connection.request('POST', '/api', params)
      #  response = connection.getresponse()
      #  data = response.read()
      #  print data
      #except:
      #  print response.status, response.reason
        
if __name__ == '__main__':
  main()