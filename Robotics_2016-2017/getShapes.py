import cv2
import numpy as np

shape = "idk"

vid = cv2.VideoCapture(1)

visionState = 1

a = 0

while True:

    ret, frame = vid.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    greenMin = np.array([70, 20, 100], dtype=np.uint8)
    greenMax = np.array([100, 255, 255], dtype=np.uint8)
    getGreen = cv2.inRange(hsv, greenMin, greenMax)

    blur = cv2.medianBlur(getGreen, 15)

    thresh, dst = cv2.threshold(blur, 220, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours != 0):
        for i in contours:
            x, y, w, h = cv2.boundingRect(contours[i])
            a = 

    for i in contours:
        curv = cv2.arcLength(i, True)
        sides = cv2.approxPolyDP(i, 0.04 * curv, True)

        if len(sides) == 3:
            shape = 'triangle'
        elif len(sides) == 4:
            shape = 'square'


    if cv2.waitKey(1) == ord('b'):
        visionState += 1
    elif cv2.waitKey(1) == ord('q'):
        break

    if visionState % 2 == 0:
        show = blur
    else:
        show = frame

    cv2.imshow('thing', show)

    print(shape)

    shape = 'idk'

vid.release()
cv2.destroyAllWindows()
