# -*- coding: utf-8 -*-

import threading, datetime, time, os, json, glob, httplib, urllib2, pickle
import config, data, helpers

class ReportBuilder(threading.Thread):
  """
  Class for threads which build a report from most recent sensor data.
  """
  
  def __init__(self, tick = 1, report_dict = data.report_dict, gps_dict = data.gps_dict, acc_dict = data.acc_dict, report_queue = data.report_queue):
    """
    Initialize the thread with tick and references to data dictionaries.
                    
    @param tick -- time the thread will sleep in seconds (defaults to 1 second)   
    @param report_dict -- reference to a dictionary which will hold the current report
    @param gps_dict -- reference to a dictionary which holds current gps data
    @param acc_dict -- reference to a dictionary which holds current accelerometer data
    @param report_queue -- reference to a queue which stores the reports
    """
    
    threading.Thread.__init__(self)
    self.running = True 
    self.tick = tick
    self.report_dict = report_dict
    self.gps_dict = gps_dict
    self.acc_dict = acc_dict
    self.report_queue = report_queue
    self.counter = 0 # this only makes sense for a singleton design pattern ...
    
    print 'ReportingBuilder initialisiert.'
    
  def run(self):
    """
    Build a report and put it in a FIFO queue.
    """
    
    while self.running:
      time.sleep(self.tick)  
      
      self.counter += 1 
      self.report_dict['counter'] = self.counter
      self.report_dict['time'] = helpers.ToIso(helpers.UtcNow()) 
      self.report_dict['gps_fixtime'] = self.gps_dict['fixtime']
      self.report_dict['gps_latitude'] = self.gps_dict['latitude']
      self.report_dict['gps_longitude'] = self.gps_dict['longitude']
      
      if self.gps_dict['mode'] == '3D': # find a way to assure the quality of gps data
        self.report_dict['gps_altitude'] = self.gps_dict['altitude']
        self.report_dict['gps_speed'] = self.gps_dict['speed']
      else:
        self.report_dict['gps_altitude'] = None
        self.report_dict['gps_speed'] = None
      
      self.report_dict['gps_mode'] = self.gps_dict['mode']
      self.report_dict['gps_satellites'] = self.gps_dict['satellites']
        
      self.report_dict['acc_axis_x'] = self.acc_dict['axis_x']
      self.report_dict['acc_axis_y'] = self.acc_dict['axis_y']
      self.report_dict['acc_axis_z'] = self.acc_dict['axis_z']
      
      self.report_queue.put(self.report_dict.copy())
      
class ReportDispatcher(threading.Thread):
  """
  Class for threads which consumes reports from a queue, stores
  """
  
  def __init__(self, trip_dict = data.trip_dict, report_queue = data.report_queue):
    """
    Initialize the thread with tick.
                    
    @param trip_dict -- reference to a dictionary which holds alle reports for the trip
    @param report_queue -- reference to a queue which stores the reports
    """
    
    threading.Thread.__init__(self)
    self.running = True 
    self.trip_dict = trip_dict
    self.report_queue = report_queue
    
    self.trip_dict['time_start']= helpers.ToIso(helpers.UtcNow())  
    
    print 'ReportDispatcher initialisiert.'

  def run(self):
    """
    Consume items from the queue and build a json trip report.
    Save final report to the filesystem and send it to the server via http.
    """
      
    self.trip_dict['time_end']= helpers.ToIso(helpers.UtcNow())  
    # consume queue items
    templist = []
    while self.report_queue.empty() == False:
      templist.append(self.report_queue.get())
      self.report_queue.task_done()
    self.trip_dict['reports'] = templist
    
    # write data to json file (preventing data loss if the http connection breaks)
    try:
      filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
      fullpath = os.path.join(config.local_path_trips, filename)
      with open(fullpath + '.json', 'w') as outfile:
        json.dump(self.trip_dict, outfile)
    except:
      raise
    
    try:
      url = 'http://' + config.server_addr + config.server_apipath
      request = urllib2.Request(url)
      request.add_header('Content-Type', 'application/json')
      response = urllib2.urlopen(request, json.dumps(self.trip_dict))
      print response
    except:
      raise
    
    