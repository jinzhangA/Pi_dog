import cv2
import pygame
import os
import RPi.GPIO as GPIO
import numpy
from datetime import datetime
import time
from imutils import encodings
from time import sleep
from motor_control import pwm_motor
from wheel import Wheel
# from car import Car
import socket
import pickle



class FaceDetector:
	def __init__(self, faceCascadePath):
		# load the face detector
		self.faceCascade = cv2.CascadeClassifier(faceCascadePath)

	def detect(self, image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)):
		# detect faces in the image
		rects = self.faceCascade.detectMultiScale(image, scaleFactor=scaleFactor,
			minNeighbors=minNeighbors, minSize=minSize)#, flags=cv2.cv.CV_HAAR_SCALE_IMAGE)

		# return the bounding boxes around the faces in the image
		return rects



camera = cv2.VideoCapture(0)
camera.set(3,320)
camera.set(4,240)
cascade_path = 'cascades/haarcascade_frontalface_default.xml'
facedetector = FaceDetector(cascade_path)
capture = 0
color = (0, 255, 0)

# GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...
# GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.add_event_detect(27, GPIO.FALLING, callback = GPIO27_callback, bouncetime = 300)
go = True
total = 0
error = (0, 0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
t_start = time.time()
frame_count = 0
while go:
	# try:
	frame_count += 1

	(grabbed, frame) = camera.read()
	frame_rate = frame_count/(time.time() - t_start)
	print "frame rate: %.1f"%frame_rate
	if not grabbed:
		break

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faceRects = facedetector.detect(gray, scaleFactor=1.1, minNeighbors=9, minSize=(10, 10))
	if len(faceRects) > 0:
		# print 'hello'
		(x, y, w, h) = max(faceRects, key=lambda b:(b[2] * b[3]))
		center = (x+0.5*w, y+0.5*h)
 		error = (160-center[0], 120-center[1])
 		print error
 		
 		
		# face = gray[y:y + h, x:x + w].copy(order="C")
		# draw bounding box on the frame
		# cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
	else: error = (0, 0)
	message = pickle.dumps(error)
 	sock.sendto(message, ('localhost', 8089))

	cv2.imshow("Frame", frame)

	key = cv2.waitKey(1) & 0xFF
	
	if key == ord("q"):
		break

camera.release()
cv2.destroyAllWindows()

