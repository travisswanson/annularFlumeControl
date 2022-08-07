from nanpy import DallasTemperature
from nanpy import (ArduinoApi, SerialManager)
import serial
from nanpy.arduinoboard import arduinomethod
from nanpy.classinfo import check4firmware
import time
from datetime import datetime

connection = SerialManager()
sensors = DallasTemperature(2, 'COM3', connection)

a = ArduinoApi(connection=connection)

n_sensors = sensors.getDeviceCount()
sensors.setResolution(12)

a.pinMode(7, a.OUTPUT)

print("There are %d devices connected on pin %d" % (n_sensors, sensors.pin))

addresses = []

for i in range(n_sensors):
    addresses.append(sensors.getAddress(i))

onOrOff = 0
file1 = open('temperatureRecord.txt','a')

for i in range(int(12*60*(60/4))):
    t = time.time()
    sensors.requestTemperatures()
    for i in range(n_sensors):
        temp = sensors.getTempC(i)
        print("Device %d (%s) temperature, in Celsius degrees is %0.2f" % (i, addresses[i], temp))
        print("Let's convert it in Fahrenheit degrees: %0.2f" % DallasTemperature.toFahrenheit(temp))
    print("\n")

    a.digitalWrite(7, (onOrOff))
    if onOrOff:
        onOrOff = 0
    else:
        onOrOff = 1

    now = datetime.now()
    currentTime = now.strftime("%d/%m/%y %H:%M:%S")
    L = str(i) + ',' + currentTime + ',' + str(sensors.getTempC(0)) + ',' + str(sensors.getTempC(1))
    file1.write(L + ' \n')

    time.sleep(15)

file1.close()