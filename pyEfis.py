#!/usr/bin/env python

#  Copyright (c) 2013 Phil Birkelbach
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

import sys
sys.path.insert(0, './lib/AeroCalc-0.11/')

import Queue
import argparse
import ConfigParser  # configparser for Python 3
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from decimal import *
from aerocalc import std_atm

import fix
import gauges
import ai
import hsi
import airspeed
import altimeter
import fgfs
import vsi
import rasp
import pa
import tc

global global_test
# This is a container object to hold the callback for the FIX thread
# which when called emits the signals for each parameter


class FlightData (QObject):
    rollChanged = pyqtSignal(float, name="rollChanged")
    pitchChanged = pyqtSignal(float, name="pitchChanged")
    headingChanged = pyqtSignal(float, name="headingChanged")
    altitudeChanged = pyqtSignal(float, name="altitudeChanged")
    airspeedChanged = pyqtSignal(float, name="airspeedChanged")
    vsiChanged = pyqtSignal(float, name="vsiChanged")
    RPMChanged = pyqtSignal(float, name="RPMChanged")
    MAPChanged = pyqtSignal(float, name="MAPChanged")
    OilPressChanged = pyqtSignal(float, name="OilPressChanged")
    OilTempChanged = pyqtSignal(float, name="OilTempChanged")
    FuelFlowChanged = pyqtSignal(float, name="FuelFlowChanged")
    FuelQtyChanged = pyqtSignal(float, name="FuelQtyChanged")
    #Changed = pyqtSignal(float, name="Changed")

    def getParameter(self, param):
        if param.name == "Roll Angle":
            self.rollChanged.emit(param.value)
        elif param.name == "Pitch Angle":
            self.pitchChanged.emit(param.value)
        elif param.name == "Heading":
            self.headingChanged.emit(param.value)
        elif param.name == "Indicated Altitude":
            self.altitudeChanged.emit(param.value)
        elif param.name == "Vertical Speed":
            self.vsiChanged.emit(param.value)
        elif param.name == "Calibrated Airspeed":
            self.airspeedChanged.emit(param.value)
        elif param.name == "N1 or Engine RPM #1":
            self.RPMChanged.emit(param.value)
        elif param.name == "Manifold Pressure #1":
            self.MAPChanged.emit(param.value)
        elif param.name == "Oil Pressure #1":
            self.OilPressChanged.emit(param.value)
        elif param.name == "Oil Temperature #1":
            self.OilTempChanged.emit(param.value)
        elif param.name == "Fuel Flow #1":
            self.FuelFlowChanged.emit(param.value)
        elif param.name == "Fuel Quantity #1":
            self.FuelQtyChanged.emit(param.value)


class main(QMainWindow):
    def __init__(self, test, parent=None):
        super(main, self).__init__(parent)
        resolution = QDesktopWidget().screenGeometry()
        config = ConfigParser.RawConfigParser()
        config.read('config')
        self.screen = config.getboolean("Screen", "screenFullSize")
        if self.screen:
            self.height = resolution.height()
            self.width = resolution.width()
        else:
            self.width = int(config.get("Screen", "screenSize.Width"))
            self.height = int(config.get("Screen", "screenSize.Height"))
        self.screenColor = config.get("Screen", "screenColor")
        self.canAdapter = config.get("CAN-FIX", "canAdapter")
        self.canDevice = config.get("CAN-FIX", "canDevice")
        self.queue = Queue.Queue()
        self.queue2 = Queue.Queue()
        self.start = 0
        if self.screen:
            self.showFullScreen()

        if test == 'normal':
            self.flightData = FlightData()
            self.cfix = fix.Fix(self.canAdapter, self.canDevice)
            self.cfix.setParameterCallback(self.flightData.getParameter)
        self.setupUi(self, test)


    def setupUi(self, MainWindow, test):
        MainWindow.setObjectName("PFD")
        MainWindow.resize(self.width, self.height)
        w = QWidget(MainWindow)
        w.setGeometry(0, 0, self.width, self.height)

        p = w.palette()
        if self.screenColor:
            p.setColor(w.backgroundRole(), QColor(self.screenColor))
            w.setPalette(p)
            w.setAutoFillBackground(True)
        instWidth = self.width - 160
        if self.height <= 480:
            instHeight = self.height - 80
        else:
            instHeight = self.height - 100
        self.a = ai.AI(w)
        self.a.resize(instWidth, instHeight)
        self.a.move(0, 20)
        
        self.alt_tape = altimeter.Altimeter_Tape(w)
        self.alt_tape.resize(70, instHeight)
        self.alt_tape.move(instWidth - 70, 20)

        self.alt_Trend = vsi.Alt_Trend_Tape(w)    
        self.alt_Trend.resize(10, instHeight)
        self.alt_Trend.move(instWidth - 80, 20)

        self.alt_setting = altimeter.Altimeter_Setting(w)    
        self.alt_setting.resize(90, 50)
        self.alt_setting.move(instWidth - 80, instHeight + 20)

        self.as_tape = airspeed.Airspeed_Tape(w)    
        self.as_tape.resize(70, instHeight)
        self.as_tape.move(0, 20)

        self.as_Trend = vsi.AS_Trend_Tape(w)    
        self.as_Trend.resize(10, instHeight)
        self.as_Trend.move(70, 20)

        self.asd_Box = airspeed.Airspeed_Mode(w)    
        self.asd_Box.resize(90, 50)
        self.asd_Box.move(0, instHeight + 20)
        
        self.head_tape = hsi.DG_Tape(w)    
        self.head_tape.resize(instWidth - 160, 60)
        self.head_tape.move(80, instHeight + 20)

        self.tC_Tape = tc.TurnCoordinator_Tape(w)
        self.tC_Tape.resize(instWidth / 4, 18)
        self.tC_Tape.move((instWidth - (instWidth / 4))/2, 1)

        if test == 'rasp':

            self.ias_warning = pa.Panel_Annunciator(w)
            self.ias_warning.setWARNING_Name("IAS")
            self.ias_warning.resize(70, 20)
            self.ias_warning.move(w.width()- 155, 310)

            self.gyro_warning = pa.Panel_Annunciator(w)
            self.gyro_warning.setWARNING_Name("Gyro")
            self.gyro_warning.resize(70, 20)
            self.gyro_warning.move(w.width()- 75, 310)

            self.mag_warning = pa.Panel_Annunciator(w)
            self.mag_warning.setWARNING_Name("Mag")
            self.mag_warning.resize(70, 20)
            self.mag_warning.move(w.width()- 155, 340)
            
            self.alt_warning = pa.Panel_Annunciator(w)
            self.alt_warning.setWARNING_Name("Alt")
            self.alt_warning.resize(70, 20)
            self.alt_warning.move(w.width()- 75, 340)

            self.cat_warning = pa.Panel_Annunciator(w)
            self.cat_warning.setWARNING_Name("CAT")
            self.cat_warning.resize(70, 20)
            self.cat_warning.move(w.width()- 155, 370)

            self.oat_warning = pa.Panel_Annunciator(w)
            self.oat_warning.setWARNING_Name("OAT")
            self.oat_warning.resize(70, 20)
            self.oat_warning.move(w.width()-75, 370)
            
            self.co = gauges.HorizontalBar(w)
            self.co.name = "Carbon Monoxide"
            self.co.units = "ppm"
            self.co.decimalPlaces = 0
            self.co.lowRange = 0.0
            self.co.highRange = 75.0
            self.co.highWarn = 25.0
            self.co.highAlarm = 50.0
            self.co.lowWarn = 0.0
            self.co.lowAlarm = 0.0
            self.co.resize(150, 70)
            self.co.move(w.width() - 155, 20)
            self.co.value = 0

            self.volt = gauges.HorizontalBar(w)
            self.volt.name = "Volt"
            self.volt.units = "V"
            self.volt.decimalPlaces = 1
            self.volt.lowRange = 9.0
            self.volt.highRange = 16.0
            self.volt.highWarn = 12.9
            self.volt.highAlarm = 14.0
            self.volt.lowWarn = 10.0
            self.volt.lowAlarm = 9.6
            self.volt.resize(150, 70)
            self.volt.move(w.width()- 155, 90)
            self.volt.value = 12

            self.cat = gauges.HorizontalBar(w)
            self.cat.name = "Cockpit air temp"
            self.cat.units = "degC"
            self.cat.decimalPlaces = 1
            self.cat.lowRange = -40.0
            self.cat.highRange = 40.0
            self.cat.highWarn = 30.0
            self.cat.highAlarm = 35.0
            self.cat.lowWarn = -20
            self.cat.lowAlarm = -30
            self.cat.resize(150, 70)
            self.cat.move(w.width()- 155, 160)
            self.cat.value = 15

            self.oat = gauges.HorizontalBar(w)
            self.oat.name = "Outside air temp"
            self.oat.units = "degC"
            self.oat.decimalPlaces = 1
            self.oat.lowRange = -40.0
            self.oat.highRange = 40.0
            self.oat.highWarn = 30.0
            self.oat.highAlarm = 35.0
            self.oat.lowWarn = -20
            self.oat.lowAlarm = -30
            self.oat.resize(150, 70)
            self.oat.move(w.width()- 155, 230)
            self.oat.value = 15

        else:
            
            self.map_g = gauges.RoundGauge(w)
            self.map_g.name = "MAP"
            self.map_g.decimalPlaces = 1
            self.map_g.lowRange = 0.0
            self.map_g.highRange = 30.0
            self.map_g.highWarn = 28.0
            self.map_g.highAlarm = 29.0
            self.map_g.resize(155, 100)
            self.map_g.move(w.width() - 155, 100)

            self.rpm = gauges.RoundGauge(w)
            self.rpm.name = "RPM"
            self.rpm.decimalPlaces = 0
            self.rpm.lowRange = 0.0
            self.rpm.highRange = 2800.0
            self.rpm.highWarn = 2600.0
            self.rpm.highAlarm = 2760.0
            self.rpm.resize(155, 100)
            self.rpm.move(w.width() - 155, 0)

            self.op = gauges.HorizontalBar(w)
            self.op.name = "Oil Press"
            self.op.units = "psi"
            self.op.decimalPlaces = 1
            self.op.lowRange = 0.0
            self.op.highRange = 100.0
            self.op.highWarn = 90.0
            self.op.highAlarm = 95.0
            self.op.lowWarn = 45.0
            self.op.lowAlarm = 10.0
            self.op.resize(150, 75)
            self.op.move(w.width() - 155, 220)
            self.op.value = 45.2

            self.ot = gauges.HorizontalBar(w)
            self.ot.name = "Oil Temp"
            self.ot.units = "degF"
            self.ot.decimalPlaces = 1
            self.ot.lowRange = 160.0
            self.ot.highRange = 250.0
            self.ot.highWarn = 210.0
            self.ot.highAlarm = 230.0
            self.ot.lowWarn = None
            self.ot.lowAlarm = None
            self.ot.resize(150, 75)
            self.ot.move(w.width() - 155, 300)
            self.ot.value = 215.2

            self.fuel = gauges.HorizontalBar(w)
            self.fuel.name = "Fuel Qty"
            self.fuel.units = "gal"
            self.fuel.decimalPlaces = 1
            self.fuel.lowRange = 0.0
            self.fuel.highRange = 50.0
            self.fuel.lowWarn = 2.0
            self.fuel.resize(150, 75)
            self.fuel.move(w.width() - 155, 380)
            self.fuel.value = 15.2

            self.ff = gauges.HorizontalBar(w)
            self.ff.name = "Fuel Flow"
            self.ff.units = "gph"
            self.ff.decimalPlaces = 1
            self.ff.lowRange = 0.0
            self.ff.highRange = 20.0
            self.ff.highWarn = None
            self.ff.highAlarm = None
            self.ff.lowWarn = None
            self.ff.lowAlarm = None
            self.ff.resize(150, 75)
            self.ff.move(w.width() - 155, 460)
            self.ff.value = 5.2

            cht = gauges.HorizontalBar(w)
            cht.name = "Max CHT"
            cht.units = "degF"
            cht.decimalPlaces = 0
            cht.lowRange = 0.0
            cht.highRange = 500.0
            cht.highWarn = 380
            cht.highAlarm = 400
            cht.resize(150, 75)
            cht.move(w.width() - 155, 540)
            cht.value = 350

            self.egt = gauges.HorizontalBar(w)
            self.egt.name = "Avg EGT"
            self.egt.units = "degF"
            self.egt.decimalPlaces = 0
            self.egt.lowRange = 0.0
            self.egt.highRange = 1500.0
            self.egt.resize(150, 75)
            self.egt.move(w.width() - 155, 620)
            self.egt.value = 1350

        if test == 'normal':
            self.flightData.pitchChanged.connect(self.a.setPitchAngle)
            self.flightData.rollChanged.connect(self.a.setRollAngle)
            self.flightData.headingChanged.connect(self.head_tape.setHeading)
            self.flightData.altitudeChanged.connect(self.alt_tape.setAltimeter)
            self.flightData.altitudeChanged.connect(self.alt_Trend.setAlt_Trend)
            #self.flightData.vsiChanged.connect(self.alt_Trend.setAlt_Trend)
            self.flightData.airspeedChanged.connect(self.as_tape.setAirspeed)
            self.flightData.airspeedChanged.connect(self.as_Trend.setAS_Trend)
            self.flightData.airspeedChanged.connect(self.asd_Box.setIAS)
            self.flightData.RPMChanged.connect(self.rpm.setValue)
            self.flightData.MAPChanged.connect(self.map_g.setValue)
            self.flightData.OilPressChanged.connect(self.op.setValue)
            self.flightData.OilTempChanged.connect(self.ot.setValue)
            self.flightData.FuelFlowChanged.connect(self.ff.setValue)
            self.flightData.FuelQtyChanged.connect(self.fuel.setValue)

        elif test == 'fgfs':
            self.timer = QTimer()
            #Timer Signal to run guiUpdate
            QObject.connect(self.timer,
                               SIGNAL("timeout()"), self.guiUpdate)
            # Start the timer 1 msec update
            self.timer.start(6)

            self.thread1 = fgfs.UDP_Process(self.queue)
            self.thread1.start()

        elif test == 'rasp':
            self.timer = QTimer()
            #Timer Signal to run guiUpdate
            QObject.connect(self.timer,
                               SIGNAL("timeout()"), self.guiUpdate)
            # Start the timer 1 msec update
            self.timer.start(5)

            self.thread1 = rasp.GPIO_Process(self.queue)
            self.thread1.start()

            self.thread2 = rasp.VW(self.queue2)
            self.thread2.start()

    def MSL_Altitude(self, pressure_alt):
        MSL_atl = pressure_alt - std_atm.press2alt(
                                    self.alt_setting.getAltimeter_Setting())
        return MSL_atl

    def guiUpdate(self):
        """
        Pull messages from the Queue and updates the Respected gauges.
        """
        try:
            msg = self.queue.get(0)
            msg2 = self.queue2.get(0)
            msg = msg.split(',')
            msg2 = msg2.split(',')
            
            if global_test == 'rasp':
                try:
                    if msg2 is not None
                        self.as_tape.setAirspeed(float(msg2[0]))
                        self.asd_Box.setAS_Data(float(msg2[0]), int(msg[4]), float(msg[6]))
                        self.as_Trend.setAS_Trend(float(msg2[0]))
                        self.oat.setValue(float(msg2[1]))
                        self.ias_warning.setState(int(msg2[2]))
                        self.oat_warning.setState(int(msg2[3]))
                    else
                        self.as_tape.setAirspeed(float(msg[0]))
                        self.asd_Box.setAS_Data(float(msg[0]), int(msg[4]), float(msg[6]))
                        self.as_Trend.setAS_Trend(float(msg[0]))
                        self.oat.setValue(float(msg[9]))
                        self.ias_warning.setState(int(msg[10]))
                        self.oat_warning.setState(int(msg[14]))
                        
                        
                    self.a.setPitchAngle(float(msg[1]))
                    self.a.setRollAngle(float(msg[2]))
                    self.head_tape.setHeading(float(msg[3]))
                    self.alt_tape.setAltimeter(self.MSL_Altitude(int(msg[4])))
                    self.alt_Trend.setAlt_Trend(float(msg[4]))
                    self.co.setValue(float(msg[5]))
                    self.volt.setValue(float(msg[6]))
                    self.cat.setValue(float(msg[7]))
                    self.alt_setting.setAltimeter_Setting(float(msg[8]))
                    self.gyro_warning.setState(int(msg[11]))
                    self.mag_warning.setState(int(msg[12]))
                    self.alt_warning.setState(int(msg[13]))
                    self.cat_warning.setState(int(msg[15]))
                    
                except:
                    pass
            else:
                try:
                    self.as_tape.setAirspeed(float(msg[0]))
                    if self.asd_Box.getMode() == 2:
                        self.asd_Box.setAS_Data(float(msg[15]), float(msg[4]),
                                                 float(msg[18]))
                    else:
                        self.asd_Box.setAS_Data(float(msg[0]), float(msg[4]),
                                                float(msg[18]))
                    self.a.setPitchAngle(float(msg[1]))
                    self.a.setRollAngle(float(msg[2]))
                    self.head_tape.setHeading(float(msg[3]))
                    self.alt_tape.setAltimeter(self.MSL_Altitude(float(msg[4])))
                    self.as_Trend.setAS_Trend(float(msg[0]))
                    self.alt_Trend.setAlt_Trend(float(msg[4]))
                    self.op.setValue(float(msg[10]))
                    self.ot.setValue(float(msg[9]))
                    self.egt.setValue(float(msg[11]))
                    self.ff.setValue(float(msg[12]))
                    self.rpm.setValue(int(float(msg[7])))
                    self.map_g.setValue(float(msg[8]))
                    self.fuel.setValue(float(msg[13]) + float(msg[14]))
                     #('Lat: ', msg[16], 'Long: ', msg[17])
                except:
                    pass

        except Queue.Empty:
            pass

    def closeEvent(self, event):
        try:
            self.thread1.stop()
            self.thread1.join(0)
            self.thread2.stop()
            self.thread2.join(0)
        except:
            pass

    def keyReleaseEvent(self, event):
        #  Increase Altimeter Setting
        if event.key() == Qt.Key_BracketLeft:
            self.alt_setting.setAltimeter_Setting(
                                self.alt_setting.getAltimeter_Setting() + 0.01)

        #  Decrease Altimeter Setting
        elif event.key() == Qt.Key_BracketRight:
            self.alt_setting.setAltimeter_Setting(
                                self.alt_setting.getAltimeter_Setting() - 0.01)

        #  Decrease Altimeter Setting
        elif event.key() == Qt.Key_M:
            self.asd_Box.setMode(self.asd_Box.getMode() + 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(description='pyEfis')
    parser.add_argument('-m', '--mode', choices=['normal', 'fgfs', 'rasp'],
        default='normal', help='Run pyEFIS in specific mode')

    args = parser.parse_args()
    print("Starting in %s Mode" % (args.mode,))
    global_test = args.mode
    form = main(args.mode)
    form.show()

    if args.mode == 'normal':
        form.cfix.start()

    result = app.exec_()
    if args.mode == 'normal':
        form.cfix.quit()
    sys.exit(result)
