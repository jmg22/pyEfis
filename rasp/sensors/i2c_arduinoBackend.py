#!/usr/bin/python

import time
import struct
import math
from Adafruit_I2C import Adafruit_I2C

# ===========================================================================
# ARDUINO Class
# ===========================================================================

class ARDUINO :
  i2c = None


  # Constructor
  def __init__(self, address=0x04, bus=1):
    self.i2c = Adafruit_I2C( 0x04 )
    self.address = address

  def bytetostr(self, lstData):
    sData = ''
    for aByte in lstData:
      sData = sData + chr(aByte)
    fmt = "<%dI" % (len(sData) // 4)
    f_data, = struct.unpack("<f",sData)
    return f_data

  def readIAS(self):
    #time.sleep(0.100)
    self.i2c.write8( 0x00, 0x01 )
    time.sleep(0.100)
    lstData =  self.i2c.readList( 0x00, 4 )
    fias = self.bytetostr(lstData)
    return fias

  def readAlt(self):
    #time.sleep(0.100)
    self.i2c.write8( 0x00, 0x02 )
    time.sleep(0.100)
    lstData =  self.i2c.readList( 0x00, 4 )
    alt = self.bytetostr(lstData)
    return alt

  def readCO(self):
    #time.sleep(0.100)
    self.i2c.write8( 0x00, 0x03 )
    time.sleep(0.100)
    lstData =  self.i2c.readList( 0x00, 4 )
    co = self.bytetostr(lstData)
    return co

  def readVolt(self):
    #time.sleep(0.100)
    self.i2c.write8( 0x00, 0x04 )
    time.sleep(0.100)
    lstData =  self.i2c.readList( 0x00, 4 )
    volt = self.bytetostr(lstData)
    return volt

  def readCAT(self):
    #time.sleep(0.100)
    self.i2c.write8( 0x00, 0x05 )
    time.sleep(0.100)
    lstData =  self.i2c.readList( 0x00, 4 )
    cat = self.bytetostr(lstData)
    return cat

  def readOAT(self):
    #time.sleep(0.100)
    self.i2c.write8( 0x00, 0x07 )
    time.sleep(0.100)
    lstData =  self.i2c.readList( 0x00, 4 )
    oat = self.bytetostr(lstData)
    return oat

if __name__=="__main__":
	ard = ARDUINO()
	print str(ard.readAlt()) + " ft"
	print str(ard.readIAS()) + " kt"
