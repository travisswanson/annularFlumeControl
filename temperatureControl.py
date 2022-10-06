from nanpy import DallasTemperature
from nanpy import (ArduinoApi, SerialManager)
import serial
from nanpy.arduinoboard import arduinomethod
from nanpy.classinfo import check4firmware
import time
from datetime import datetime


def temperatureControl(tI, comPort, tempInfo):
    # Arduino pins for equipment control
    dallasSensorPin = 2
    heatPin = 7
    coolingPin = 8

    # Tolerance for "seeking" goal temperature
    tempTol = 0.5

    try:
        connection = SerialManager(comPort)
    except Exception:
        print("Ardunio was not found.")
        print("terminating image collection")
        print("terminating flume temperature control")
        # if the serial connection cannot start, send termination signal to other processes
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
        goalTemp = f2c(tempInfo['lowTemp'])

        tempPeriod = tempInfo['tempPeriod'] * 60 * 60  # change from seconds to hours

        lowTemp = f2c(tempInfo['lowTemp'])
        highTemp = f2c(tempInfo['highTemp'])

        chillerRunning = False
        heaterRunning = False

        tmpObs = 0

        # begin temperature control loop
        while tI.value == 1:

            t = time.time()

            if t - tOld >= tempPeriod:
                tOld = t
                if goalTemp == lowTemp:
                    goalTemp = highTemp
                else:
                    goalTemp = lowTemp

            #read temperatures
            sensors.requestTemperatures()
            # 0 - tank
            # 1 - flume effulent
            # 2 - GW effulent
            # 3 - air temperature

            temp = []
            for k in range(n_sensors):
                tmp = sensors.getTempC(k)
                temp.append(tmp)
                # print("Device %d (%s) temperature, in Celsius degrees is %0.2f" % (k, addresses[k], tmp))
                # print("Let's convert it in Fahrenheit degrees: %0.2f" % DallasTemperature.toFahrenheit(tmp))
                # print("\n")

            now = datetime.now()
            currentTime = now.strftime("%d/%m/%y %H:%M:%S")

            L = str(tmpObs) + ',' + currentTime + ',' + str(sensors.getTempC(0)) + ',' + str(
                sensors.getTempC(1)) + ',' + str(sensors.getTempC(2)) + ',' + str(sensors.getTempC(3))
            file1.write(L + ' \n')
            print('System Temperatures: Tank- {}, flume ef.- {}, GW ef.- {}, Lab air- {}'.format(temp[0], temp[1],
                                                                                                 temp[2], temp[3]))

            print('Temperature Goal: {}, Tank: {}'.format(goalTemp, temp[0]))

            if goalTemp > temp[0]:
                # flume temperature is too cold, add heat
                if heaterRunning:
                    # Equipment is running, keep adding heat
                    print("Heating- Temperature: {} is outside of tolerance {}".format(temp[0], goalTemp))
                    a.digitalWrite(heatPin, 1)
                    a.digitalWrite(coolingPin, 0)
                    heaterRunning = True
                    chillerRunning = False

                elif not heaterRunning:
                    # equipment is not running, turn on heat if difference is outside of tolerance
                    if abs(goalTemp - temp[0]) > tempTol:
                        print("Heating- Temperature: {} is outside of tolerance {}".format(temp[0], goalTemp))
                        a.digitalWrite(heatPin, 1)
                        a.digitalWrite(coolingPin, 0)
                        heaterRunning = True
                        chillerRunning = False
                    else:
                        # flume temperature is in tolerance, turn off equipment/ keep equipment off
                        print("Flume temperature is in tolerance - {}".format(temp[0]))

                        a.digitalWrite(heatPin, 0)
                        a.digitalWrite(coolingPin, 0)
                        heaterRunning = False
                        chillerRunning = False
                        print('Temperature is within tolerance, equipment off')

            elif goalTemp < temp[0]:
                # flume temperature is too hot, remove heat

                if chillerRunning:
                    # Equipment is running, keep removing heat
                    print("Cooling- Temperature: {} is outside of tolerance {}".format(temp[0], goalTemp))
                    a.digitalWrite(heatPin, 0)
                    a.digitalWrite(coolingPin, 1)
                    chillerRunning = True
                    heaterRunning = False

                elif not chillerRunning:
                    # equipment is not running, turn on chiller if difference is outside of tolerance
                    if abs(goalTemp - temp[0]) > tempTol:
                        print("Cooling- Temperature: {} is outside of tolerance {}".format(temp[0], goalTemp))
                        a.digitalWrite(heatPin, 0)
                        a.digitalWrite(coolingPin, 1)
                        chillerRunning = True
                        heaterRunning = False
                    else:
                        # flume temperature is in tolerance, turn off equipment/ keep equipment off
                        print("Flume temperature is in tolerance - {}".format(temp[0]))

                        a.digitalWrite(heatPin, 0)
                        a.digitalWrite(coolingPin, 0)
                        print('Temperature is within tolerance, equipment off')
                        chillerRunning = False
                        heaterRunning = False

            print("{} temperature record written".format(tmpObs))
            tmpObs += 1
            time.sleep(60)

        # End of run, tI.value has been changed, and loop is exited

        print('Temperature Control ending, shutting off equipment...')
        # end of program, make sure that heating and cooling are off
        a.digitalWrite(heatPin, 0)
        a.digitalWrite(coolingPin, 0)
        heaterRunning = False
        chillerRunning = False
        print('End of run - Temperature control equipment shut off')

        file1.close()
