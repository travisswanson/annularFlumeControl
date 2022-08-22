import time
import flumeControl
import captureImage
import temperatureControl
import multiprocessing
import os
import cv2
import datetime
import numpy as np
import serial
import serial.tools.list_ports


def main():
  
    noExp = 10
    VHG = '0MM'
    expDuration = 5 #hours
    tempControlComPort = 'COM3'
    flumeControlComPort = 'COM4'
    tempInfo = {'lowTemp': 75,
                'highTemp': 85,
                'tempPeriod': 2}



    for exp in range(noExp):
        print('Starting exp: {} ... '.format(exp))
        dir2save = 'C:/Users/User/Documents/flumeImagery/' + str(expDuration) + '_hr/' + VHG + 'V' + str(exp)
        if os.path.exists(dir2save):
            os.chdir(dir2save)
            print('Working directory changed to: {} ... '.format(dir2save))
        else:
            print('Making new directory...')
            os.makedirs(dir2save)
            print("The new directory is created!")
            os.chdir(dir2save)
            print('Working directory changed to: {} ... '.format(dir2save))

        print("{} : {} ".format("Experiment", exp), flush=True)

        spinSpeed = multiprocessing.Value('i', 0)
        takeImages = multiprocessing.Value('i', 1)
        expCount = multiprocessing.Value('i', exp)

        P0 = multiprocessing.Process(target=captureImage.captureImage, args=[spinSpeed, takeImages])
        P1 = multiprocessing.Process(target=flumeControl.flumeControl, args=[spinSpeed, takeImages, expCount, expDuration, flumeControlComPort])
        P2 = multiprocessing.Process(target=temperatureControl.temperatureControl, args=[takeImages, tempControlComPort, tempInfo] )

        P0.start()
        P1.start()
        P2.start()

        # wait for all processes to complete, motor control before images, of course
        P1.join()
        P0.join()
        P2.join()

        print("Experimental Run {} is complete..".format(exp))

    print('Total Experiment Program complete...')


if __name__ == '__main__':
    main()
