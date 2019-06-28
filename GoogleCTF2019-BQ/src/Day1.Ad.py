#!/usr/bin/python
import cv2

cap = cv2.VideoCapture('y2mate.mp4')
i = 0
while True:
    res, frame = cap.read()
    if not res:
        break
    cv2.imwrite("frames/{:03d}.jpg".format(i), frame)
    i += 1

cap.release()
