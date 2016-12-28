#  Copyright (c) 2016 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from instruments import ai
from instruments import gauges
from instruments import hsi
from instruments import airspeed
from instruments import altimeter
from instruments import vsi
from instruments import pa
from instruments import tc

class Screen(QWidget):
    def __init__(self, parent=None):
        super(Screen, self).__init__(parent)
        self.parent = parent
        p = self.parent.palette()

        self.screenColor = (0,0,0)
        if self.screenColor:
	        p.setColor(self.backgroundRole(), QColor(self.screenColor))
        	self.setPalette(p)
        	self.setAutoFillBackground(True)
		
		#Atitude indicator
        self.ai = ai.AI(self)
        self.ai.fontSize = 20
        self.ai.pitchDegreesShown = 60
		
		#Altimeter
        self.alt_tape = altimeter.Altimeter_Tape(self)
	self.alt_Box = altimeter.Altimeter_Digit(self)
        self.alt_Trend = vsi.Alt_Trend_Tape(self)
        self.alt_setting = altimeter.Altimeter_Setting(self)
        
        #Airspeed indicator
        self.as_tape = airspeed.Airspeed_Tape(self)
	self.asdi_Box = airspeed.Airspeed_Digit(self)
	self.asd_Box = airspeed.Airspeed_Mode(self)
		
		#Vertical speed indicator
        self.as_Trend = vsi.AS_Trend_Tape(self)
        
        #HSI
        self.head_tape = hsi.DG_Tape(self)
        
        #Slip indicator
        self.tC_Tape = tc.Slip_Tape(self)


		#System Voltage
	self.volt = gauges.HorizontalBar(self)
        self.volt.name = "Volt"
        self.volt.decimalPlaces = 1
        self.volt.dbkey = "VOLT"
		
		#Cockpit air temp
	self.cat = gauges.HorizontalBar(self)
        self.cat.name = "Cockpit air temp"
        self.cat.decimalPlaces = 1
        self.cat.dbkey = "CAT"
		
		#Outside air temp
	self.oat = gauges.HorizontalBar(self)
        self.oat.name = "Outside air temp"
        self.oat.decimalPlaces = 1
        self.oat.dbkey = "OAT"
	
	self.ias_warning = pa.Panel_Annunciator(self)
        self.ias_warning.setWARNING_Name("IAS")

        self.gyro_warning = pa.Panel_Annunciator(self)
        self.gyro_warning.setWARNING_Name("Gyro")

        self.mag_warning = pa.Panel_Annunciator(self)
        self.mag_warning.setWARNING_Name("Mag")
            
        self.alt_warning = pa.Panel_Annunciator(self)
        self.alt_warning.setWARNING_Name("Alt")

        self.cat_warning = pa.Panel_Annunciator(self)
        self.cat_warning.setWARNING_Name("CAT")

        self.oat_warning = pa.Panel_Annunciator(self)
        self.oat_warning.setWARNING_Name("OAT")



    def resizeEvent(self, event):
        instWidth = self.width() - 160
        instHeight = self.height() - 80
        self.ai.move(0, 20)
        self.ai.resize(instWidth, instHeight)

        self.alt_tape.resize(70, instHeight)
        self.alt_tape.move(instWidth -70, 20)

	self.alt_Box.resize(60, 25)
        self.alt_Box.move(instWidth - 69,(instHeight / 2) + 7.5)

        self.alt_Trend.resize(10, instHeight)
        self.alt_Trend.move(instWidth - 80 , 20)

        self.as_tape.resize(70, instHeight)
        self.as_tape.move(0, 20)

	self.asdi_Box.resize(45, 25)
        self.asdi_Box.move(25, (instHeight / 2) + 7.5)

        self.as_Trend.resize(10, instHeight)
        self.as_Trend.move(70, 20)

        self.asd_Box.resize(90, 20)
        self.asd_Box.move(0, 0)

        self.head_tape.resize(instWidth, 60)
        self.head_tape.move(0, instHeight + 20)

        self.alt_setting.resize(90, 20)
        self.alt_setting.move(instWidth -80, 0)
        
        self.tC_Tape.resize(instWidth / 4, 18)
        self.tC_Tape.move((instWidth - (instWidth / 4))/2, 1)
        
        self.volt.resize(150, 70)
        self.volt.move(self.width()- 155, 90)
        
        self.cat.resize(150, 70)
        self.cat.move(self.width()- 155, 160)
        
        self.oat.resize(150, 70)
        self.oat.move(self.width()- 155, 230)
        
        self.ias_warning.resize(70, 20)
        self.ias_warning.move(self.width()- 155, 310)
        
        self.gyro_warning.resize(70, 20)
        self.gyro_warning.move(self.width()- 75, 310)
        
        self.mag_warning.resize(70, 20)
        self.mag_warning.move(self.width()- 155, 340)
        
        self.alt_warning.resize(70, 20)
        self.alt_warning.move(self.width()- 75, 340)
        
        self.cat_warning.resize(70, 20)
        self.cat_warning.move(self.width()- 155, 370)
        
        self.oat_warning.resize(70, 20)
        self.oat_warning.move(self.width()-75, 370)
