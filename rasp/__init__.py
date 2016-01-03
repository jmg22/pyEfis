#This file takes in inputs from a variety of sensor files , and outputs information
import sys
sys.dont_write_bytecode = True
#import numpy as np
import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os
from sys import exit
import threading
from rasp.sensors import sensor
from collections import deque

class VW(threading.Thread):

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.queue = conn
        self.ias = 0
        self.oat = 0
        self.ias_W_S = 0
        self.oat_W_S = 0
        self.smooted = 0.8
        if not os.path.isfile('/home/pi/pyEfis/rasp/virtualwire.cfg'):
                        print "Unable to access config file: virtualwire.cfg"
                        exit(1)
        sensorConfig = ConfigParser.SafeConfigParser()
        sensorConfig.read('/home/pi/pyEfis/rasp/virtualwire.cfg')
        i="VirtualWire"
        sensorNames = sensorConfig.sections()
        if i in sensorNames:
            try:
                enabled = sensorConfig.getboolean(i,"enabled")
            except Exception:
                enabled = True
        if enabled:
            from rasp.sensors import vwBackend
            import pigpio
            rxpin = int(sensorConfig.get(i,"rxpin"))
            bps = int(sensorConfig.get(i,"bps"))
            pigpio.exceptions = False
            self.pi = pigpio.pi() # Connect to local Pi
            self.rx = vwBackend.rx(self.pi, rxpin, bps) # Specify Pi, rx GPIO.
            self.running = 1

    def run(self):
        print "Virtualwire thread started"
        while self.running:
            time.sleep(0.3)
            try:
                while self.rx.ready():
                    try:
                        msg = str("".join(chr (c) for c in self.rx.get()))
                    except:
                        pass
                msg = msg.split(',')
                if float(msg[0]) < 400 :
                    ias = float(msg[0])
                    self.ias = float((self.ias*self.smooted)+(1.0-self.smooted)*(ias))
                    self.ias_W_S = 3
                if float(msg[1]) > -50 :                   
                    self.oat = float(msg[1])
                    self.oat_W_S = 3
                else:
                    self.ias_W_S = 2
                    self.oat_W_S = 2
            except:
                pass
            data = [self.ias, self.oat, self.ias_W_S, self.oat_W_S]
            data_test = str(data).strip('[]')
            self.queue.put(data_test)
    
    def stop(self):
        self.rx.cancel()
        self.pi.stop()
        self.running = 0

class GPIO_Process(threading.Thread):


    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.queue = conn
        self.hg = 29.92
        self.ias = 0
        self.pitch = 0
        self.roll = 0
        self.heading = 0
        self.alt = 0
        self.co = 0
        self.volt = 12
        self.cat = 0
        self.oat = 0
        self.alt_W_S = 0
        self.cat_W_S = 0
        self.gyro_W_S = 0
        self.heading_W_S = 0
        self.ias_W_S = 0
        self.oat_W_S = 0
        self.smooted = 0.7
       
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
                        #raise e
        self.running = 1


    def run(self):
        cat_sample = 0    
        oat_sample = 0                               
        while self.running:                    
                data = []
                #Collect the data from each sensor
                for i in self.sensorPlugins:
                        dataDict = {}
                        val = i.getVal()
                        if val==None: #this means it has no data to upload.
                                continue
                        dataDict["name"] = i.valName
                        dataDict["sensor"] = i.sensorName
                        if dataDict["name"] == "IAS":
                            try:
                                ias_Value = i.getVal()
                                if self.ias < 200:
                                    self.ias = int((self.alt*self.smooted)+(1.0-self.smooted)*(ias_Value))
                                    self.ias_W_S = 3
                                elif  not (200 <= self.ias >= 250):
                                    self.ias_W_S = 1
                                else:
                                    self.ias = 0
                                    self.ias_W_S = 2
                            except:
                                pass
                        elif dataDict["name"] == "Orientation":
                                msg = i.getVal()
                                msg = str(msg).strip('[]')
                                msg = msg.split(',')
                                if int(msg[0]) != 1000:
                                    self.heading = int(msg[0])
                                    self.roll = int(msg[1])
                                    self.pitch = int(msg[2])
                                    self.heading_W_S = 3
                                    self.roll_W_S = 3
                                    self.pitch_W_S = 3
                                else:
                                    self.heading_W_S = 2
                                    self.roll_W_S = 2
                                    self.pitch_W_S = 2
                                #print msg
                        elif dataDict["name"] == "Altitude":
                            try:
                                alt_Value = i.getVal()
                                if alt_Value < 10000:
                                    self.alt = int((self.alt*self.smooted)+(1.0-self.smooted)*(alt_Value))
                                    self.alt_W_S = 3
                                elif  not (10000 <= alt_Value >= 12500):
                                    self.alt = int((self.alt*self.smooted)+(1.0-self.smooted)*(alt_Value))
                                    self.alt_W_S = 1
                                else:
                                    self.alt = 0
                                    self.alt_W_S = 2
                            except:
                                pass
                            #print self.alt
                        elif dataDict["name"] == "Carbon_Monoxide":
                            try:
                                self.co = i.getVal()
                                if self.co < 1000:
                                    self.co_W_S = 3
                                else:
                                    self.co = 1000
                                    self.co_W_S = 2
                            except:
                                pass
                        elif dataDict["name"] == "Volt":
                                self.volt = i.getVal()
                                #print self.volt
                        elif dataDict["name"] == "CAT":
                            cat_sample += 1
                            if cat_sample >= 5:
                                try:
                                    self.cat = i.getVal()
                                    cat_sample = 0
                                    if self.cat > -50:
                                        self.cat_W_S = 3
                                    else:
                                        self.cat_W_S = 2
                                except:
                                    pass
                            #print self.cat
                        elif dataDict["name"] == "hg":
                                self.hg = i.getVal()
                        elif dataDict["name"] == "OAT":
                            oat_sample += 1
                            if oat_sample >= 5:
                                try:
                                    self.oat = i.getVal()
                                    oat_sample = 0
                                    if self.oat > -50:
                                        self.oat_W_S = 3
                                    else:
                                        self.oat_W_S = 2
                                except:
                                    pass
                            #print self.oat
                        data.append(dataDict)
                working = True
                if working != True:
                        print "Failed to upload"
                        
                time.sleep(.25)
                data = [self.ias, self.pitch, self.roll, self.heading, self.alt, self.co, self.volt, self.cat, self.hg, self.oat, self.ias_W_S, self.gyro_W_S, self.heading_W_S, self.alt_W_S, self.oat_W_S, self.cat_W_S]
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
    q2 = queue.Queue()
    t2 = VW(q2)
    t2.start()
    t2.join()
