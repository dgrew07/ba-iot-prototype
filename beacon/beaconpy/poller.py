# -*- coding: utf-8 -*-

import threading, math, smbus, time
from gps import *
import config, data, helpers

class GpsPoller(threading.Thread):
  """
  Class for threads which poll data from the gps dongle.
  """
  
  def __init__(self, tick = 0, gps_dict = data.gps_dict):
    """
    Initialize the thread with gps object and tick.
                   
    @param tick -- time the thread will sleep in seconds (defaults to 0 seconds) 
    @param gps_dict -- reference to a dictionary which will hold current gps data
    """
    
    threading.Thread.__init__(self)
    self.running = True 
    self.tick = tick
    self.gps_dict = gps_dict
    # init session object with gps moddule
    self.session = gps(mode=WATCH_ENABLE) 
    
    print 'GpsPoller initialisiert.'

  def run(self):
    """
    Poll the serial gps interface and write values to data module when avaiable.
    """

    while self.running:
      # get values from the gps dongle
      # since this is a serial interface, next() has to be called repeatedly in order to get the latest values
      # next() also blocks, which makes time.sleep() obsolete
      # time between gps-fixes is usually between 1-3 seconds
      self.session.next() 
      
      # write latest gps data to referenced dict
      try:
        self.gps_dict['fixtime'] = helpers.ToIso(self.session.fix.time)
        
        if hasattr(self.session.fix, 'latitude'):
          if math.isnan(self.session.fix.latitude) != True:
            self.gps_dict['latitude'] = self.session.fix.latitude
          else:
            self.gps_dict['latitude'] = None
          
        if hasattr(self.session.fix, 'longitude'):
          if math.isnan(self.session.fix.longitude) != True:
            self.gps_dict['longitude'] = self.session.fix.longitude
          else:
            self.gps_dict['longitude'] = None
          
        if hasattr(self.session.fix, 'altitude'):
          if math.isnan(self.session.fix.altitude) != True:
            self.gps_dict['altitude'] = self.session.fix.altitude
          else:
            self.gps_dict['altitude'] = None
          
        if hasattr(self.session.fix, 'speed'):
          if math.isnan(self.session.fix.speed) != True:
            self.gps_dict['speed'] = self.session.fix.speed
          else:
            self.gps_dict['speed'] = None
        # decode mode value
        if self.session.fix.mode == 3:
          self.gps_dict['mode'] = '3D'
        elif self.session.fix.mode == 2:
          self.gps_dict['mode'] = '2D'
        elif self.session.fix.mode == 1:
          self.gps_dict['mode'] = 'kein Fix'
        else:
          self.gps_dict['mode'] = 'kein Wert'
        self.gps_dict['satellites'] = len(self.session.satellites)
        
      except:
        print 'Fehler beim schreiben der GPS-Daten!'
        raise
      
class AccPoller(threading.Thread):
  """
  Class for threads which poll data from MPU-6050 accelerometer.
  """
  
  def __init__(self, tick = 0, acc_dict = data.acc_dict, power_mgmt_1 = 0x6b, power_mgmt_2 = 0x6c, bus = 2, address = 0x68, addr_x = 0x3b, addr_y = 0x3d, addr_z = 0x3f, offs_x = 0, offs_y = 0, offs_z = 0):
    """
    Initialize the thread with tick and i2c-device params.
    Run i2cdetect in shell to get the base address.
                    
    @param tick -- time the thread will sleep in seconds (defaults to 0 seconds)   
    @param acc_dict -- reference to a dictionary which will hold current accelerometer data
    @param power_mgmt_1 -- power management register 1 (defaults to 0x6b)   
    @param power_mgmt_2 -- power management register 2 (defaults to 0x6c)   
    @param bus -- i2c device bus (defaults to 2)   
    @param address -- i2c address (defaults to 0x68)   
    @param addr_x -- x-value register of the accelerometer (defaults to 0x3b)
    @param addr_y -- y-value register of the accelerometer (defaults to 0x3d)
    @param addr_z -- z-value register of the accelerometer (defaults to 0x3f)
    @param offs_x -- calibration offset for x-values (raw value, defaults to 0)
    @param offs_y -- calibration offset for y-values (raw value, defaults to 0)
    @param offs_z -- calibration offset for z-values (raw value, defaults to 0)
    """
    
    threading.Thread.__init__(self)
    self.running = True 
    self.tick = tick
    self.acc_dict = acc_dict
    self.power_mgmt_1 = power_mgmt_1 # power management register
    self.power_mgmt_2 = power_mgmt_2 # power management register
    self.bus = smbus.SMBus(bus) # this is the i2d-device number e.g. /dev/i2c-2
    self.address = address # this is the address value read via i2cdetect command
    self.addr_x = addr_x 
    self.addr_y = addr_y # see read_number() for more info on the value registers
    self.addr_z = addr_z
    self.offs_x = offs_x
    self.offs_y = offs_y # see calibration package or main method for mor info on offsets
    self.offs_z = offs_z
    
    self.session = helpers.Bunch(raw = None, scaled = None)
    self.session.raw = helpers.Bunch(x = None, y = None, z = None)
    self.session.scaled = helpers.Bunch(x = None, y = None, z = None)
    
    self.bus.write_byte_data(self.address, self.power_mgmt_1, 0) # wake mpu 6050 from sleep mode (IMPORTANT!)
    
    print 'AccPoller initialisiert.'

  def read_number(self, adr):
    """
    Read two 8bit registers of an i2c device and add them, which gives a 16bit number in two's complement. 
    
    @param adr -- register address
    @return 16bit number in two's complement
    """
    
    high = self.bus.read_byte_data(self.address, adr)
    low = self.bus.read_byte_data(self.address, adr + 1)
    val = (high << 8) + low # shift high 8 bits to the left and add low
    return val

  def read_number2c(self, adr):
    """
    Transform a 16bit number (two's complement ) to an integer.
    
    @param adr -- register address
    @return integer (+/- 32768)
    """
    
    val = self.read_number(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
        
  def scale_number(self, gforce = 9.81, range = 2):
    """
    Calculate scaling factor dependig on range of the accelerometer and the used value for 1G in m/s^2.
    If no given range matches the MPU-6050 range modes, the default range +/- 2G is used.
    
    @param gforce -- value for 1G in m/s^2 (defaults to 9.81)
    @param range -- set range, either 2, 4, 8 or 16 (defaults to 2)
    @return acceleration in m/s^2 (float)
    """
    
    if range == 2:
      return gforce / 16384
    elif range == 4: 
      return gforce / 8192
    elif range == 8: 
      return gforce / 4096
    elif range == 16: 
      return gforce / 2048
    else: 
      return gforce / 16384

  def run(self):
    """
    Poll the serial i2c interface, scale the raw values and write them to the data module.
    """
    
    scaler = self.scale_number(config.acc_oneg, config.acc_range)
    while self.running:
      # read, scale and write data
      self.session.raw.x = self.read_number2c(self.addr_x) - self.offs_x
      self.session.raw.y = self.read_number2c(self.addr_y) - self.offs_y
      self.session.raw.z = self.read_number2c(self.addr_z) - self.offs_z
      self.session.scaled.x = self.session.raw.x * scaler
      self.session.scaled.y = self.session.raw.y * scaler
      self.session.scaled.z = self.session.raw.z * scaler
      self.acc_dict['axis_x'] = self.session.scaled.x
      self.acc_dict['axis_y'] = self.session.scaled.y
      self.acc_dict['axis_z'] = self.session.scaled.z
      
      time.sleep(self.tick) 