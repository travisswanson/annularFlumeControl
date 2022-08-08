import serial
import serial.tools.list_ports
import time
import numpy as np
import datetime

def flumeControl(mSpeed, tI, eC, eD, comPort):

    def runSegment(ard, runTime, motorSpeed, finalSpeed, spinDir, noSteps, file1, ex):
        t = time.time()
        speedVec = np.ceil(spinDir * np.linspace(motorSpeed, finalSpeed, noSteps)).astype(int)

        timeStep = runTime / speedVec.size
        oldSpeed = speedVec[0] - 1
        mSpeed.value = speedVec[0]
        for x in np.nditer(speedVec):
            mSpeed.value = x
            if (oldSpeed != x):
                ard.flush()
                msg2send = str(x) + '\n'
                ard.write(msg2send.encode())
                oldSpeed = x
            now = datetime.datetime.now()
            currentTime = now.strftime("%d/%m/%y %H:%M:%S")
            L = 'Exp #: ' + str(ex) + ' Value sent: ' + str(x) + ' ' + str(
                round((time.time() - t) / 60, 2)) + ' min  Time: ' + currentTime
            print(L)
            file1.write(L + ' \n')
            time.sleep(timeStep)

    print('Opening a new text file...')
    file1 = open('0mmV' + str(eC.value) + '.txt', 'a')

    #print('Looking for an Arduino...')
    #ports = list(serial.tools.list_ports.comports())
    #deviceFound = False
    #for p in ports:
    #    print(p)
    #    print(p.description)
    #    if "Arduino" in p.description:
    #        port = p.device
    #        print("found an Arduino on " + port)
    #        deviceFound = True
            
    #if not deviceFound:
    #    print("Ardunio was not found.")
    #    print("terminating image collection")
    #    tI.value = 0
    #else:
    try:
        ard = serial.Serial(comPort, 9600, timeout=5)
    except:
        print("Ardunio was not found.")
        print("terminating image collection")
        print("terminating flume temperature control")
        tI.value = 0
    else:
        # sleep a little so the Arduino has a chance to catch up
        time.sleep(2)

        # Configuration of experimental run
        spinDir = 1
        initialSpeed = 0
        finalSpeed = 3000
        runTime = 60*2
        noSteps = 10
        runSegment(ard, runTime, initialSpeed, finalSpeed, spinDir, noSteps, file1, eC.value)

        initialSpeed = 3000
        finalSpeed = 3000
        runTime = 60*60*1
        noSteps = 30
        runSegment(ard, runTime, initialSpeed, finalSpeed, spinDir, noSteps, file1, eC.value)

        initialSpeed = 3000
        finalSpeed = 800
        runTime = 60*60*eD
        noSteps = 60*eD
        runSegment(ard, runTime, initialSpeed, finalSpeed, spinDir, noSteps, file1, eC.value)

        ard.close()
        file1.close()
        print('Ending image collection...')
        time.sleep(2)
        tI.value = 0
