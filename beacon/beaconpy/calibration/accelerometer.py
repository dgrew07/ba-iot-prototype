# -*- coding: utf-8 -*-
# calibration/accelerometer.py

import os, time, smbus, math

"""Calibration script for the accelerometer."""

"""
  Calculate the tripple axis offsets from expected readings.  
  x-axis should read zero.
  y-axis should read zero.
  z-axis should read 1g = 9.81 m/s^2.
  
  @param power_mgmt_1 -- power management register 1 (defaults to 0x6b)   
  @param power_mgmt_2 -- power management register 2 (defaults to 0x6c)   
  @param bus -- i2c device bus (defaults to 2)   
  @param address -- i2c address (defaults to 0x68)   
  @param addr_x -- x-value register of the accelerometer (defaults to 0x3b)
  @param addr_y -- y-value register of the accelerometer (defaults to 0x3d)
  @param addr_z -- z-value register of the accelerometer (defaults to 0x3f)   
  @return object of offsets e.g. offsets.x
  """
def calibrate_acc(power_mgmt_1 = 0x6b, power_mgmt_2 = 0x6c, bus = 2, address = 0x68, addr_x = 0x3b, addr_y = 0x3d, addr_z = 0x3f): 
  os.system('clear') 

  print '  MPU-6050 Accelerometer Kalibrierungsskript                 '
  print '-------------------------------------------------------------'
  print 
  print '  Den Sensor bitte moeglichst horizontal positionieren!      '
  time.sleep(1)
  print '  ..                                                         '
  time.sleep(1)
  print '  ....                                                       '
  time.sleep(1)
  print '  ......                                                     '
  time.sleep(1)
  print 
  print '  Die Kalibrierung beginnt ...                               '
  time.sleep(1)

  #power_mgmt_1 = 0x6b
  #power_mgmt_2 = 0x6c

  devbus = smbus.SMBus(bus) 
  #address = 0x68       

  devbus.write_byte_data(address, power_mgmt_1, 0)

  print 
  print '  Daten werden gesammelt, bitte warten...                    '

  i = 0
  buffersize = 10000
  mean_ax = 0
  mean_ay = 0
  mean_az = 0
  buff_ax = 0
  buff_ay = 0
  buff_az = 0

  err_acc = 8

  while i < (buffersize + 101):
    if i > 100 and i <= (buffersize + 100):
      buff_ax += read_number2c(devbus, address, addr_x)
      buff_ay += read_number2c(devbus, address, addr_y)
      buff_az += read_number2c(devbus, address, addr_z)
    if i == (buffersize + 100):
      mean_ax = buff_ax / buffersize
      mean_ay = buff_ay / buffersize
      mean_az = buff_az / buffersize
    i += 1

  offsets = Bunch(x = mean_ax, y = mean_ay, z = mean_az)

  print 
  print '  Fertig!                                                    '
  print '-------------------------------------------------------------'
  print
  print '  Accelerometer Offsets                                      '
  print '-------------------------------------------------------------'
  print '  Fehlertoleranz (raw)               ' , err_acc
  print '  Fehlertoleranz (skaliert)          ' , err_acc/16384
  print '  Fehlertoleranz (m/s^2)             ' , err_acc*(9.80665/16384)
  print 
  print '  Offset X-Achse (raw)               ' , offsets.x
  print '  Offset X-Achse (skaliert)          ' , offsets.x/16384
  print '  Offset X-Achse (m/s^2)             ' , offsets.x*(9.80665/16384)
  print 
  print '  Offset Y-Achse (raw)               ' , offsets.y
  print '  Offset Y-Achse (skaliert)          ' , offsets.y/16384
  print '  Offset Y-Achse (m/s^2)             ' , offsets.y*(9.80665/16384)
  print 
  print '  Offset Z-Achse (raw)               ' , offsets.z
  print '  Offset Z-Achse (skaliert)          ' , offsets.z/16384
  print '  Offset Z-Achse (m/s^2)             ' , offsets.z*(9.80665/16384)
  print '-------------------------------------------------------------'
  
  # sleep to allow reading the offsets (debugging)
  print
  print ' Warte 10 Sekunden... '
  time.sleep(10)
  
  return offsets

# TODO: dupes with functions in ../poller.py -> export into package e.g. helpers
def read_number(bus, address, adr):
  """
  Read two 8bit registers of an i2c device and add them, which gives a 16bit number in two's complement. 
  
  @param adr -- register address
  @return 16bit number in two's complement
  """
    
  high = bus.read_byte_data(address, adr)
  low = bus.read_byte_data(address, adr + 1)
  val = (high << 8) + low # shift high 8 bits to the left and add low
  return val

def read_number2c(bus, address, adr):
  """
  Transform a 16bit number (two's complement ) to an integer.
   
  @param adr -- register address
  @return integer (+/- 32768)
  """
    
  val = read_number(bus, address, adr)
  if (val >= 0x8000):
    return -((65535 - val) + 1)
  else:
    return val

class Bunch:
  """
  Helper class to init json-printable objects.
  """
  
  def __init__(self, **kwds):
    self.__dict__.update(kwds)
  def to_JSON(self):
    return json.dumps(self, default = lambda o: o.__dict__, 
      sort_keys = True)