import cv2
import numpy as np

from networktables import NetworkTables as nt
import logging

import time
#NetworkTable setup:
f = open('log.txt', 'w')
logging.basicConfig(level = logging.DEBUG)
nt.initialize(server = '10.17.81.2')
sd = nt.getTable('SmartDashboard')

#where the video feed comes from:
vidFeed = cv2.VideoCapture(1)

#changing resolution; width 320 & height 240
vidFeed.set(3, 320);
vidFeed.set(4, 240);

#change exposure
vidFeed.set(cv2.cv.CV_CAP_PROP_EXPOSURE, -50)

#keep track of biggest contour's index
tapeIndex1 = 0
tapeIndex2 = 0

#keep positions & etc of contours
x = [0, 1]
y = [0, 1]
w = [0, 1]
h = [0, 1]

#tape x-axis center:
xA = 0.0 #left POV
xB = 0.0 #right POV
yA = 0.0 #y-axis center

#tape x-axis center:
pegX = 0.0 #assigned after POV is determined
#robot uses to determine if turn right/left or move right/left:
moveRight = 0 #0 = do nothing; 1 = move right; -1 = move left

#camera default resolution:
camWidth = 640
camHeight = 480

#sensitivity to what is considered center:
centerThresh = 40

#distance between tape:
dist = 0

#distance threshold for what the distance between the tape should be
distThreshMin = 1
distThreshMax = 1.6 # if x or x1 is < 100 then this is 2 else it's 1.6
visionState = 1

#area
a = 0
biggest = 0
secondBig = 0

#keep track of time
prevTime = time.time()

#while running take video feed and process:
while True:
    #get video feed
    ret, frame = vidFeed.read()

    #convert color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #define threshold for the color we're looking for
    #hue 45-80 from testing----!!!!!!!!!!--------
    greenMin = np.array([50, 20, 30], dtype=np.uint8)
    greenMax = np.array([80, 255, 255], dtype=np.uint8)

    #filter colors not in range of threshold out and convert to binary image
    getGreen = cv2.inRange(hsv, greenMin, greenMax)

    #blur:
    #blur = cv2.medianBlur(getGreen, 5)
    blur = cv2.erode(getGreen, None, iterations=2)
    blur = cv2.dilate(blur, None, iterations=2)
    blur = cv2.medianBlur(blur, 15)

    #search binary image for whitest (our green)
    thresh, dst = cv2.threshold(blur, 220, 255, cv2.THRESH_BINARY)

    #seach through what we defined as greenn to find contours
    contours, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #area of biggest contours:
    biggest = 0
    socondBig = 0

    #if contours are found:
    if len(contours) != 0:
#-----!!!!!!!!Put rectangles over all contours found------!!!!!!!####
#----!!!!!!!!!!!!!!!!!!----Compare area of all rectangles-------!!!!!!!!!!#
        #we'll look for the biggest ones:
        for i in range(len(contours)):
            x1, y1, w1, h1 = cv2.boundingRect(contours[i])
            a = w1 * h1
            if a >= biggest:
            #    print(a, i)
                secondBig = biggest
                biggest = a
                tapeIndex2 = tapeIndex1
                tapeIndex1 = i
            elif a >= secondBig:
            #    print(a, i)
                a = secondBig
                tapeIndex2 = i
        #get the position and dimensions of the contour that we've found to be our tape
        if tapeIndex1 < len(contours) and tapeIndex2 < len(contours):
            x[0], y[0], w[0], h[0] = cv2.boundingRect(contours[tapeIndex1])
            x[1], y[1], w[1], h[1] = cv2.boundingRect(contours[tapeIndex2])
        elif tapeIndex1 >= len(contours) or tapeIndex2 >= len(contours):
            tapeIndex1 = 0
            tapeIndex2 = 0
        #put rectangles around our tape:
        cv2.rectangle(frame, (x[0], y[0]), (x[0]+w[0], y[0]+h[0]), (0, 0, 255), 2) #biggest is red
        cv2.rectangle(frame, (x[1], y[1]), (x[1]+w[1], y[1]+h[1]), (255, 0, 0), 2) #second is blue

        #x-center if left POV
        xA = x[0] + (((x[1] + w[1]) - x[0])/2)
        distXA = xA - x[0] #distance
        #x-center if right POV
        xB = x[1] + (((x[0] + w[0]) - x[1])/2)
        distXB = xB -x[1] #distance
        #y-center
        yAB = y[0] + (h[0]/2)

        #threshold change depending on where tape is found
        if x[0] < 100 or x[1] < 100:
            distThreshMax = 2.0
        else:
            distThreshMax = 1.8

        #don't consider if one tape is twice as big than the other (tape w=2 h=5)
        #the peg won't cut the bigger tape in half bc its in front so we only need
        #to consider the 2.5/5 since we're dividing the smaller by bigger so shouldn't
        #be bigger than 1 (4.99/5)
        if (h[1]+0.0)/(h[0]+0.0) > .43 and (h[1]+0.0)/(h[0]+0.0) < 1.2:
            #check if within distance for left or right POV and draw circle accordingly
            if x[1] > x[0] and  (x[1]+0.0)/(x[0]+0.0) > distThreshMin and (x[1]+0.0)/(x[0]+0.0) < distThreshMax:
                cv2.circle(frame, (xA, yAB), 5, (255, 0, 255), -1)
                pegX = xA
                prevTime = time.time()
                dist = distXA
                if pegX < camWidth/2 + centerThresh and pegX > camWidth/2 - centerThresh:
                    moveRight = 1
                elif (h[1]+0.0)/(h[0]+0.0) > .9 and (h[1]+0.0)/(h[0]+0.0) < 1.1:
                    moveRight = 0
            elif x > x1 and (x[0]+0.0)/(x[1]+0.0) > distThreshMin and (x[0]+0.0)/(x[1]+0.0) < distThreshMax:
                cv2.circle(frame, (xB, yAB), 5, (255, 0, 255), -1)
                pegX = xB
                prevTime = time.time()
                dist = distXB
                if pegX < (camWidth+0.0)/(2.0) + centerThresh and pegX > (camWidth+0.0)/(2.0) - centerThresh:
                    moveRight = -1
                elif (h[1]+0.0)/(h[0]+0.0) > .9 and (h[1]+0.0)/(h[0]+0.0) < 1.1:
                    moveRight = 0
            #check if distance is proportional to 10.25/5 = 2.05 or (tape distance)/(tape height)
            if (dist+0.0)/(h[0]+0.0) > 1.7 and (dist+0.0)/(h[0]+0.0) < 2.55:
                prevTime = time.time()
                print('updated')
                #sd.putNumber('x', pegX)
                sd.putNumber('turnDirection', moveRight)
                #print('foundX ' + str(pegX))

    #if peg position is lost and more than a second has passed
    #the gear peg position will be unknown so we'll send -1
    #otherwise send the last known position

    if time.time() - prevTime > .1:
        print('lostX')
        sd.putNumber('x', -1)
        p = str("Time: " + str(time.time()) + " / " + str(-1) + "| \n")
        f.write(p)
    else:
        print('havX: ', pegX)
        sd.putNumber('x', pegX)
        p = str("Time: " + str(time.time()) + " / " + str(pegX) + "| \n")
        f.write(p)


#    if h[0] != 0 or x[0] != 0:
#        print(a, secondBig, len(contours), (dist+0.0)/(h[0]+0.0), (h[1]+0.0)/(h[0]+0.0), (x[1]+0.0)/(x[0]+0.0), dist, h[0])

    if cv2.waitKey(1) == ord('b'):
        visionState += 1

    if visionState % 2 == 0:
        show = blur
    else:
        show = frame

    cv2.imshow('labeled', show)
        #cv2.imshow('processed', getGreen)

            #will exit if you press 'q':
    if cv2.waitKey(1) == ord('q'):
        break



vidFeed.release()
cv2.destroyAllWindows()

#!!!!!! Y val must be > 160 !!!!!!!!!!---------------------TEST-------------------------
