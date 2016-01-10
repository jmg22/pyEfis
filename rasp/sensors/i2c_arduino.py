import sensor
import time
import i2c_arduinoBackend
class ARDUINO(sensor.Sensor):
        arduinoClass = None
	requiredData = ["measurement","address"]
	optionalData = ["unit"]
	def __init__(self,data):
		self.sensorName = "Arduino"
		if "alt" in data["measurement"].lower():
                        self.valName = "Altitude"
			self.valSymbol = "Ft"
			self.valUnit = "Feet"
                        if "unit" in data:
				if data["unit"].lower in ["meter","Meter","M","m"]:
					self.valUnit = "Meter"
					self.valSymbol = "M"
		elif "co" in data["measurement"].lower():
			self.valName = "Carbon_Monoxide"
			self.valSymbol = "ppm"
			self.valUnit = "ppm"
			
		elif "ias" in data["measurement"].lower():
                        self.valName = "IAS"
			self.valSymbol = "kt"
			self.valUnit = "Kts"
                        if "unit" in data:
				if data["unit"].lower in ["mille","milles","M","m"]:
					self.valUnit = "Milles"
					self.valSymbol = "Mph"
			elif "unit" in data:
				if data["unit"].lower in ["KMH","kmh","km","k"]:
					self.valUnit = "kmh"
					self.valSymbol = "kmh"
                        
		elif "oat" in data["measurement"].lower():
			self.valName = "OAT"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			if "unit" in data:
				if data["unit"]=="F":
					self.valUnit = "Fahrenheit"
					self.valSymbol = "F"
		elif "cat" in data["measurement"].lower():
                        self.valName = "CAT"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			if "unit" in data:
				if data["unit"]=="F":
					self.valUnit = "Fahrenheit"
					self.valSymbol = "F"
                elif "volt" in data["measurement"].lower():
                        self.valName = "Volt"
			self.valSymbol = "V"
			self.valUnit = "volt"

                if (ARDUINO.arduinoClass==None):
                        ARDUINO.arduinoClass = i2c_arduinoBackend.ARDUINO(address=int(data["address"]))
                        
		return

	def getVal(self):
		if self.valName == "OAT":
                        try:
                                temp = ARDUINO.arduinoClass.readOAT()
                        except:
                                temp = -50
                                pass
			if self.valUnit == "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp
		elif self.valName == "CAT":
                        try:
                                temp = ARDUINO.arduinoClass.readCAT()
                        except:
                                temp = -50
                                pass
			if self.valUnit == "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp
		
		elif self.valName == "Altitude":
                        try:
                                alt = ARDUINO.arduinoClass.readAlt()
                        except:
                                alt = 15000
                                pass
                        if self.valUnit == "Feet":
				alt = round(alt * 3.28084)
                        return int(alt)	
                elif self.valName == "Carbon_Monoxide":
                        try:
                                co = ARDUINO.arduinoClass.readCO()
                        except:
                                co = 1000
                                pass
                        return int(co)
                elif self.valName == "IAS":
                        global ias
                        try:
                                ias = ARDUINO.arduinoClass.readIAS()
                                ias = round(ias)
                        except:
                                #ias = 1000
                                pass
                        if self.valUnit == "Milles":
				ias = int(round(ias * 1.15078))
			elif self.valUnit == "kmh":
				ias = int(round(ias * 1.852))
			return ias
                elif self.valName == "Volt":
                        try:
                                volt = ARDUINO.arduinoClass.readVolt()
                        except:
                                volt = 1000
                                pass
                        return float(volt)
