from nanpy import DallasTemperature
from nanpy import (ArduinoApi, SerialManager)
import serial
from nanpy.arduinoboard import arduinomethod
from nanpy.classinfo import check4firmware
import time
from datetime import datetime


def temperatureControl(tI, comPort, tempInfo):
    dallasSensorPin = 2
    heatPin = 7
    coolingPin = 8
    tempTol = 0.25

    try:
        connection = SerialManager(comPort)
    except Exception:
        print("Ardunio was not found.")
        print("terminating image collection")
        print("terminating flume temperature control")
        tI.value = 0
    else:

        sensors = DallasTemperature(dallasSensorPin, connection)
        a = ArduinoApi(connection=connection)

        n_sensors = sensors.getDeviceCount()
        sensors.setResolution(12)

        # heating
        a.pinMode(heatPin, a.OUTPUT)
        a.pinMode(coolingPin, a.OUTPUT)

        print("There are %d devices connected on pin %d" % (n_sensors, sensors.pin))

        addresses = []

        for i in range(n_sensors):
            addresses.append(sensors.getAddress(i))

        file1 = open('temperatureRecord.txt', 'a')

        # make a quick function to change Fahrenheit to Celsius
        f2c = lambda a: (a - 32) * (5 / 9)

        tOld = time.time()
        goalTemp = f2c(tempInfo['highTemp'])
        tempPeriod = tempInfo['tempPeriod'] * 60 * 60  # change from seconds to hours
        lowTemp = f2c(tempInfo['lowTemp'])
        highTemp = f2c(tempInfo['highTemp'])
        tmpObs = 0

        while tI.value == 1:

            t = time.time()

            if t - tOld >= tempPeriod:
                tOld = t
                if goalTemp == lowTemp:
                    goalTemp = highTemp
                else:
                    goalTemp = lowTemp

            sensors.requestTemperatures()
            temp = []
            for k in range(n_sensors):
                tmp = sensors.getTempC(k)
                temp.append(tmp)
                # print("Device %d (%s) temperature, in Celsius degrees is %0.2f" % (k, addresses[k], tmp))
                # print("Let's convert it in Fahrenheit degrees: %0.2f" % DallasTemperature.toFahrenheit(tmp))
                # print("\n")

            now = datetime.now()
            currentTime = now.strftime("%d/%m/%y %H:%M:%S")
            L = str(tmpObs) + ',' + currentTime + ',' + str(sensors.getTempC(0)) + ',' + str(sensors.getTempC(1))
            file1.write(L + ' \n')
            print('Temperature- Goal: {}, Current: {}'.format(goalTemp, temp[0]))

            if abs(goalTemp - temp[0]) > tempTol:
                # flume temperature is out of tolerance, do something

                if goalTemp > temp[0]:
                    # flume temperature is too cold, add heat
                    a.digitalWrite(heatPin, 1)
                    a.digitalWrite(coolingPin, 0)
                    print('Switching to heating...')

                elif goalTemp < temp[0]:
                    # flume temperature is too hot, remove heat
                    a.digitalWrite(heatPin, 0)
                    a.digitalWrite(coolingPin, 1)
                    print('Switching to cooling...')
            else:
                # flume temperature is in tolerance, turn off equipment
                print("Flume temperature is in tolerance - {}".format(temp[0]))

                a.digitalWrite(heatPin, 0)
                a.digitalWrite(coolingPin, 0)
                print('Temperature is within tolerance, equipment off')

            print("{} temperature record written".format(tmpObs))
            tmpObs += 1
            time.sleep(15)

        print('Temperature Control ending, shutting off equipment')
        # end of program, make sure that heating and cooling are off
        a.digitalWrite(heatPin, 0)
        a.digitalWrite(coolingPin, 0)
        print('Temperature control equipment shut off')

        file1.close()