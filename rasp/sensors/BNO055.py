
import sensor
import bnoBackend

class BNO055(sensor.Sensor):
	bnoClass = None
	requiredData = ["measurement","rst"]
	optionalData = ["unit"]
	def __init__(self, data):
                self.statusSample = 0
                self.sys = 0
		self.sensorName = "BNO055"
		if "euler" in data["measurement"].lower():
			self.valName = "Orientation"
			self.valUnit = "degre"
			self.valSymbol = ""
			
		elif "temp" in data["measurement"].lower():
			self.valName = "Temperature"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			if "unit" in data:
				if data["unit"]=="F":
					self.valUnit = "Fahrenheit"
					self.valSymbol = "F"
			
		if (BNO055.bnoClass==None):
                        try:
                                BNO055.bnoClass = bnoBackend.BNO055(serial_port='/dev/ttyAMA0', rst=int(data["rst"]))
                        except:
                                pass
                if not BNO055.bnoClass.begin():
                        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
                        bnoClass = None
                        pass
                        return 

	def getVal(self):
		if self.valName == "Orientation":
                        try:
                                heading, roll, pitch = BNO055.bnoClass.read_euler()
                                x,y,z = BNO055.bnoClass.read_accelerometer()
                                #print heading, roll, pitch
                                if pitch >= 90:
                                        pdiff = pitch - 90
                                        pitch = 90 - pdiff
                                        if roll > 0:
                                                roll = -(roll - 180)
                                        else:
                                                roll = -(roll + 180)
                                elif pitch <= -90:
                                        mpdiff = pitch + 90
                                        pitch = -(90 + mpdiff)
                                        if roll > 0:
                                                roll = -(roll - 180)
                                        else:
                                                roll = -(roll + 180)
                                if heading >= 180:
                                        heading = heading - 180
                                else:
                                        heading = heading + 180
                                if self.statusSample >= 200:       
                                        self.sys, gyro, accel, mag = BNO055.bnoClass.get_calibration_status()
                                        self.statusSample = 0
                                else:
                                        self.statusSample = self.statusSample + 1
                        except:
                                pass
                        return [heading, roll, pitch, self.sys, x]
                        
		elif self.valName == "Temperature":
			temp = BNO055.bnoClass.read_temp()
			if self.valUnit == "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp

	def getSysState(self):
                try:
                        status, self_test, error = BNO055.bnoClass.get_system_status()
                except:
                        status = 1000
                        self_test = 1000
                        error = 1000
                        pass
		return [status, self_test, error]

	def getCalState(self):
                try:
                        sys, gyro, accel, mag = BNO055.bnoClass.get_calibration_status()
                except:
                        sys = 1000
                        gyro = 1000
                        accel = 1000
                        mag = 1000
                        pass
		return [sys, gyro, accel, mag]
		
