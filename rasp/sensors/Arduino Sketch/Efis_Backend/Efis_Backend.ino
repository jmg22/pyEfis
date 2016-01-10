#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <CS_MQ7.h>
#include <VirtualWire.h>
#undef int
#undef abs
#undef double
#undef float
#undef round
boolean bmp085;
boolean vwReceived = false;
char received[100];
char data[30];
float cat;
float alt;
float ias;
float oat;
float volt;
float hgSet;
char msg[30];
CS_MQ7 MQ7(12, 13);  // 12 = digital Pin connected to "tog" from sensor board// 13 = digital Pin connected to LED Power Indicator
Adafruit_BMP085 bmp;
int CoSensorOutput = 0; //analog Pin connected to "out" from sensor board
int CoData = 0;         //analog sensor data

// déclaration des registres
byte regs[3];
int regIndex = 0; // Registre à lire ou à écrire.
byte lastExecReq = 0x00;

void setup()
{
  pinMode(13, OUTPUT);
  regs[0] = 0x00; // reg0 = registre d'exécution
  regs[1] = 0x00;
  regs[2] = 0x00;
  Wire.begin(4);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  pinMode( 13, OUTPUT );
  digitalWrite( 13, HIGH );
  vw_set_ptt_inverted(true);
  vw_set_rx_pin(12);
  vw_setup(2000);	 // Bits per sec
  vw_rx_start();       // Start the receiver PLL running
  //testBmp();
}

void loop()
{
  uint8_t buf[VW_MAX_MESSAGE_LEN];
  uint8_t buflen = VW_MAX_MESSAGE_LEN;
  if (vw_get_message(buf, &buflen))
  {
    vwReceived = true;
    digitalWrite(13, HIGH);
    int i;
    for (i = 0; i < buflen; i++)
    {
      received[i] = buf[i];
    }
    received[buflen] = '\0';
    char *test[sizeof(strtok(received, ","))];
    if (sizeof(test) > 0)
    {
      test[0] = strtok(received, ","); // Splits spaces between words in str
      ias = atof(test[0]);
      Wire_SendFloat( ias );
      for (int i = 1; i < sizeof(strtok(received, ",")); i++)
      {
        test[i] = strtok (NULL, ",");
        oat = atof(test[i]);
        Wire_SendFloat( oat );
      }
    }
    digitalWrite(13, LOW);
  }
  if ( regs[0] == 0x00 ) {
    return;
    MQ7.CoPwrCycler();
  }

  switch ( regs[0] ) {
    case 0x01 : // demande de version (rien à faire)
      break;
    case 0x02 : // demande de valeur Float (rien à faire, l'operation et retour de donnée est exécuté à la demande de réponse)
      break;
  }
  regs[0] = 0x00;
  //if (bmp085 == false)
  //{
    //testBmp();
  //}
}

void receiveEvent(int howMany)
{
  int byteCounter = 0;

  while ( byteCounter < howMany )
  {
    byte b = Wire.read();
    byteCounter += 1;
    if ( byteCounter == 1 ) { // Byte #1 = Numéro de registre
      regIndex = b;
    }
    else {                    // Byte #2 = Valeur a stocker dans le registre
      switch (regIndex) {
        case 0:
          regs[0] = b;
          lastExecReq = b;
          break;
        case 1:
          regs[1] = b;
          break;
        case 2:
          regs[2] = b;
          break;
      }
    }
  }
}

void Wire_SendFloat (float arg)
{
  byte * data = (byte *) &arg;
  Wire.write( data, sizeof (arg) );
}

void requestEvent()
{
  switch ( regIndex ) {

    case 0x00: // Indicated Air Speed and Outside Air Temperatur
      switch ( lastExecReq ) {
        case 0x01: // Indicated Air Speed
          if (vwReceived == false)
          {
            ias = 1000;
          }
          Wire_SendFloat( ias );
          break;

        case 0x02: // Altitude
          if (bmp085 == true)
          {
            alt = bmp.readAltitude();
          }
          Wire_SendFloat( alt );
          break;

        case 0x03: // Carbone monoxide
          if (MQ7.CurrentState() == LOW) { //we are at 1.4v, read sensor data!
            CoData = analogRead(CoSensorOutput);
            Wire_SendFloat( CoData );
          }
          else {                           //sensor is at 5v, heating time
            CoData = 1000;
            Wire_SendFloat( CoData );
          }
          break;

        case 0x04: // Volt
            volt = 12;
            Wire_SendFloat( volt );
          break;

        case 0x05: // Cockpit Air Temperature
          if (bmp085 == true)
          {
            cat = bmp.readTemperature();
          }
          Wire_SendFloat( cat );
          break;

        case 0x06: // Altitude Pression Adjustement
            hgSet = 29,92;
            Wire_SendFloat( hgSet );
          break;

        case 0x07: // Outside Air Temperature
          if (vwReceived == false)
          {
            oat = -50;
          }
          Wire_SendFloat( oat );
          break;

        case 0x08: // All data

          break;

        default:
          Wire.write( 0xFF ); // ecrire 255 = il y a un problème!
      }
      break;

    default: // lecture autre registre
      Wire.write( 0xFF ); // ecrire 255 = il y a un problème
  }

}

void testBmp()
{
  if (!bmp.begin()) {
    bmp085 = false;
    alt = 15000;
    cat = -50;
  }
  else
  {
    bmp085 = true;
  }
}
