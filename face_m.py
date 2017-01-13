import cv2
import pygame
import os
import RPi.GPIO as GPIO
import numpy
from datetime import datetime
from imutils import encodings
from time import sleep
import time
# from motor_control import pwm_motor
# from wheel import Wheel
# from car import Car
import socket
import pickle
import multiprocessing as mp


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
# use button 27 to exit the program
def GPIO27_callback(channel):
	print "Button 27 pressed, quit"
	exit()


camera = cv2.VideoCapture(0)
camera.set(3,320)
camera.set(4,240)
camera.set(5, 30)
# camera.set(21, 1)
cascade_path = 'cascades/haarcascade_frontalface_default.xml'
facedetector = FaceDetector(cascade_path)

GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.FALLING, callback = GPIO27_callback, bouncetime = 300)
go = True
total = 0
error = (0, 0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

def get_face_send(gray_image):
	start_time = time.time()
	faceRects = facedetector.detect(gray_image)#, scaleFactor=1.1, minNeighbors=9, minSize=(30, 30))
	if len(faceRects) > 0:
		# print 'hello'
		(x, y, w, h) = max(faceRects, key=lambda b:(b[2] * b[3]))
		center = (x+0.5*w, y+0.5*h)
 		error = (160-center[0], 120-center[1])
 		
 	else: error = (0, 0)

 	message_raw = (start_time, time.time(), error)
 	# print message_raw
	message = pickle.dumps(message_raw)
 	sock.sendto(message, ('localhost', 8089))


pool = mp.Pool( processes=4 )
frame_count = 0
(grabbed, frame) = camera.read()
print grabbed
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
processe0 = pool.apply_async( get_face_send, (gray,) )    
processe1 = pool.apply_async( get_face_send, (gray,) )    
processe2 = pool.apply_async( get_face_send, (gray,) )    
processe3 = pool.apply_async( get_face_send, (gray,) )    

processe0.get()
processe1.get()
processe2.get()
processe3.get()
sleep(2)
t_start = time.time()
frame_count = 0
while go:
	frame_count += 1
	(grabbed, frame) = camera.read()

	frame_rate = frame_count/(time.time() - t_start)
	print "frame rate: %.1f"%frame_rate
	if not grabbed:
		break
		
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	process = pool.apply_async( get_face_send, (gray,) ) 
 	process.get()
 	
 		
		# face = gray[y:y + h, x:x + w].copy(order="C")
		# draw bounding box on the frame
		# cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
	

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

camera.release()
cv2.destroyAllWindows()

