#This file takes in inputs from a variety of sensor files , and outputs information
import sys
sys.dont_write_bytecode = True
import numpy as np
import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os
from sys import exit
import threading
from rasp.sensors import sensor


class GPIO_Process(threading.Thread):


    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.queue = conn
        self.hg = 29.92
        self.speed = 34
        self.pitch = 15
        self.roll = 15
        self.heading = 180
        self.alt = 0
        self.co = 0
        self.volt = 12
        self.cat = 0
        self.alt_W_S = 2
        self.cat_W_S = 2
        self.gyro_W_S = 2
        self.mag_W_S = 2
        self.ias_W_S = 2
        self.oat_W_S = 2

        def get_subclasses(mod,cls):
                for name, obj in inspect.getmembers(mod):
                        if hasattr(obj, "__bases__") and cls in obj.__bases__:
                                return obj
        
        if not os.path.isfile('/home/pi/pyEfis/rasp/sensors.cfg'):
                        print "Unable to access config file: sensors.cfg"
                        exit(1)

        sensorConfig = ConfigParser.SafeConfigParser()
        sensorConfig.read('/home/pi/pyEfis/rasp/sensors.cfg')

        sensorNames = sensorConfig.sections()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        self.sensorPlugins = []
        for i in sensorNames:
                try:	
                        try:
                                filename = sensorConfig.get(i,"filename")
                        except Exception:
                                print("Error: no filename config option found for sensor plugin " + i)
                                raise
                        try:
                                enabled = sensorConfig.getboolean(i,"enabled")
                        except Exception:
                                enabled = True

                        #if enabled, load the plugin
                        if enabled:
                                try:
                                        mod = __import__('rasp.sensors.'+filename,fromlist=['a']) #Why does this work?
                                except Exception:
                                        print("Error: could not import sensor module " + filename)
                                        raise

                                try:	
                                        sensorClass = get_subclasses(mod,sensor.Sensor)
                                        if sensorClass == None:
                                                raise AttributeError
                                except Exception:
                                        print("Error: could not find a subclass of sensor.Sensor in module " + filename)
                                        raise

                                try:	
                                        reqd = sensorClass.requiredData
                                except Exception:
                                        reqd =  []
                                try:
                                        opt = sensorClass.optionalData
                                except Exception:
                                        opt = []

                                pluginData = {}

                                class MissingField(Exception): pass
						
                                for requiredField in reqd:
                                        if sensorConfig.has_option(i,requiredField):
                                                pluginData[requiredField]=sensorConfig.get(i,requiredField)
                                        else:
                                                print "Error: Missing required field '" + requiredField + "' for sensor plugin " + i
                                                raise MissingField
                                for optionalField in opt:
                                        if sensorConfig.has_option(i,optionalField):
                                                pluginData[optionalField]=sensorConfig.get(i,optionalField)
                                instClass = sensorClass(pluginData)
                                self.sensorPlugins.append(instClass)
                                print ("Success: Loaded sensor plugin " + i)
                except Exception as e: #add specific exception for missing module
                        print("Error: Did not import sensor plugin " + i )
                        raise e
        self.running = 1

                
    def run(self):
        def runningMean(x, N):
                    return np.convolve(x, np.ones((N,))/N)[(N-1):]
        cat_sample = 0                               
        while self.running:                    
                data = []
                #Collect the data from each sensor
                for i in self.sensorPlugins:
                        dataDict = {}
                        val = i.getVal()
                        if val==None: #this means it has no data to upload.
                                continue
                        #dataDict["value"] = i.getVal()
                        dataDict["unit"] = i.valUnit
                        dataDict["symbol"] = i.valSymbol
                        dataDict["name"] = i.valName
                        dataDict["sensor"] = i.sensorName
                        if dataDict["name"] == "Speed":
                                self.speed = i.getVal()
                        elif dataDict["name"] == "Pitch":
                                self.pitch = i.getVal()
                        elif dataDict["name"] == "Roll":
                                self.roll = i.getVal()
                        elif dataDict["name"] == "Heading":
                                self.heading = i.getVal()
                        elif dataDict["name"] == "Altitude":
                            try:
                                alt_Value = i.getVal()
                                if alt_Value < 10000:
                                    self.alt = int(runningMean(alt_Value, 3))
                                    self.alt_W_S = 3
                                elif  not (10000 <= alt_Value <= 12500):
                                    self.alt = int(runningMean(alt_Value, 3))
                                    self.alt_W_S = 1
                                else:
                                    self.alt = 0
                                    self.alt_W_S = 2
                            except ValueError:
                                pass
                                #print self.alt
                        elif dataDict["sensor"] == "MiCS-5525":
                                self.co = i.getVal()
                        elif dataDict["sensor"] == "Voltmeter":
                                self.volt = i.getVal()
                        elif dataDict["name"] == "Temperature":
                            cat_sample += 1
                            if cat_sample >= 3:
                                try:
                                    self.cat = i.getVal()
                                    cat_sample = 0
                                    if self.cat > -50:
                                        self.cat_W_S = 3
                                    else:
                                        self.cat_W_S = 2
                                except ValueError:
                                    pass
                        elif dataDict["sensor"] == "10k-pot":
                                self.hg = i.getVal()
                        data.append(dataDict)
                working = True
                if working != True:
                        print "Failed to upload"
                        
                time.sleep(.2)
                self.Panel_anouciator = 'Null'
                data = [self.speed, self.pitch, self.roll, self.heading, self.alt, self.co, self.volt, self.cat, self.hg, self.alt_W_S, self.cat_W_S, self.gyro_W_S, self.mag_W_S, self.ias_W_S, self.oat_W_S]
                data_test = str(data).strip('[]')
                self.queue.put(data_test)

    def stop(self):
        self.running = 0
                        
        

if __name__ == '__main__':
    import queue
    q = queue.Queue()
    t = GPIO_Process(q)
    t.start()
    t.join()
