![alt tag](https://raw.githubusercontent.com/jmg22/pyEfis/master/pyEfis.png)
pyEfis
==================

This is an Electronic Flight Information System written in Python.

It was created for use in the MakerPlane Open Source Aircraft Project.

pyEfis is written primarily in Python and PyQt.

It does not have any method of reading flight information in directly
from the hardware but instead uses FIX (Flight Information eXchange).
FIX is a group of technologies that specify how aircraft systems
information should be formated and exchanged.  Libraries for all the
FIX protocols will eventually be added to pyEfis, right now there
is a remedial implementation of CAN-FIX which is the FIX protocol
for CANBus.

This program is quite immature at this stage and should not be used
in an aircraft of any kind.


You connect FlightGear to pyEFIS you need to copy pyefis.xml to Protocol in the FGRoot directort.

Launch FlightGear with this command addtional
--generic=socket,out,10,IP of PC with pyEFIS,34200,udp,pyefis

Controls

'[' and ']' Keys changes the Altimeter Setting

'm' Changes Airspeed mode from IAS , TAS, and GS
