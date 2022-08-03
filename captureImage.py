import cv2
import datetime
import time

def captureImage(mSpeed, tI):
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # set new dimensionns to cam object (not cap)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    imCount = 0
    while tI.value == 1:
        print("Starting Image Collection..")
        return_value, image = camera.read()
        cv2.imwrite(
            str(imCount) + '-' + str(mSpeed.value) + '-' + datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S') + '.jpg',
            image)
        print('Just wrote jpg # ' + str(imCount) + '...')
        imCount += 1
        time.sleep(15)

    del camera
    print('Image collection completed..')