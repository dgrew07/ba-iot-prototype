#!/usr/bin/python

import os
import time
import smbus
import math

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

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

bus = smbus.SMBus(2) 
address = 0x68       

bus.write_byte_data(address, power_mgmt_1, 0)

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

offs_ax = 0
offs_ay = 0
offs_az = 0

while i < (buffersize + 101):
  if i > 100 and i <= (buffersize + 100):
    buff_ax += read_word_2c(0x3b)
    buff_ay += read_word_2c(0x3d)
    buff_az += read_word_2c(0x3f)
  if i == (buffersize + 100):
    mean_ax = buff_ax / buffersize
    mean_ay = buff_ay / buffersize
    mean_az = buff_az / buffersize
  i += 1

offs_ax = mean_ax 
offs_ay = mean_ay 
offs_az = mean_az

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
print '  Offset X-Achse (raw)               ' , offs_ax
print '  Offset X-Achse (skaliert)          ' , offs_ax/16384
print '  Offset X-Achse (m/s^2)             ' , offs_ax*(9.80665/16384)
print 
print '  Offset Y-Achse (raw)               ' , offs_ay
print '  Offset Y-Achse (skaliert)          ' , offs_ay/16384
print '  Offset Y-Achse (m/s^2)             ' , offs_ay*(9.80665/16384)
print 
print '  Offset Z-Achse (raw)               ' , offs_az
print '  Offset Z-Achse (skaliert)          ' , offs_az/16384
print '  Offset Z-Achse (m/s^2)             ' , offs_az*(9.80665/16384)
print '-------------------------------------------------------------'
