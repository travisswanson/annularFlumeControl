from nanpy import DallasTemperature
from nanpy import (ArduinoApi, SerialManager)
import serial
from nanpy.arduinoboard import arduinomethod
from nanpy.classinfo import check4firmware
import time
from datetime import datetime

def temperatureControl():


    dallasSensorPin = 2
    heatPin = 7
    coolingPin = 8
    comPort = 'COM3'

    connection = SerialManager(comPort)

    sensors = DallasTemperature(dallasSensorPin, connection)
    a = ArduinoApi(connection=connection)

    n_sensors = sensors.getDeviceCount()
    sensors.setResolution(12)

    # heating
    a.pinMode(heatPin, a.OUTPUT)

    # cooling
    a.pinMode(coolingPin, a.OUTPUT)

    print("There are %d devices connected on pin %d" % (n_sensors, sensors.pin))

    addresses = []

    for i in range(n_sensors):
        addresses.append(sensors.getAddress(i))

    onOrOff = 0
    file1 = open('temperatureRecord.txt','a')

    for i in range(int(12*60*(60/4))):
        t = time.time()
        sensors.requestTemperatures()
        for k in range(n_sensors):
            temp = sensors.getTempC(i)
            print("Device %d (%s) temperature, in Celsius degrees is %0.2f" % (k, addresses[k], temp))
            print("Let's convert it in Fahrenheit degrees: %0.2f" % DallasTemperature.toFahrenheit(temp))
        print("\n")

        now = datetime.now()
        currentTime = now.strftime("%d/%m/%y %H:%M:%S")
        L = str(i) + ',' + currentTime + ',' + str(sensors.getTempC(0)) + ',' + str(sensors.getTempC(1))
        file1.write(L + ' \n')

        if goalTemp - temp[0] > tempTol:
            # flume temperature is too cold, add heat
            a.digitalWrite(heatPin, 1)
            a.digitalWrite(coolingPin, 0)
        elif goalTemp - temp[0] < tempTol:
            # flume temperature is too hot, remove heat
            a.digitalWrite(heatPin, 1)
            a.digitalWrite(coolingPin, 0)
        else:
            # flume temperature is in tolerance, turn off equipment
            a.digitalWrite(heatPin, 0)
            a.digitalWrite(coolingPin, 0)

        print("{} temperature record written".format(i))
        time.sleep(15)

    # end of program, make sure that heating and cooling are off
    a.digitalWrite(heatPin, 0)
    a.digitalWrite(coolingPin, 0)

    file1.close()