import cv2
import os
import numpy
from imutils import encodings
from time import sleep
import time
import socket
import pickle
import multiprocessing as mp
from picamera.array import PiRGBArray
from picamera import PiCamera

camera = PiCamera()
camera.resolution = ( 320, 240 )
camera.framerate = 60

rawCapture = PiRGBArray( camera, size=( 320, 240 ) )
cascade_path = 'cascades/haarcascade_frontalface_default.xml'
facedetector = cv2.CascadeClassifier(cascade_path)

go = True
total = 0
error = (0, 0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
frame_count = 0

def get_face_send(frame):
	try:
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faceRects = facedetector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=9, minSize=(10, 10))
		if len(faceRects) > 0:
			(x, y, w, h) = max(faceRects, key=lambda b:(b[2] * b[3]))
			center = (x+0.5*w, y+0.5*h)
	 		error = (160-center[0], w-55)
	 	else: error = (None, None)
	 	print error
		message = pickle.dumps(('error', error))
	 	sock.sendto(message, ('localhost', 8089))
	except KeyboardInterrupt:
	 	global key
	 	key = ord("q")


pool = mp.Pool( processes = 3 )
sleep(2)
# t_start = time.time()
for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
	image = frame.array
	# frame_count += 1
	# frame_rate = frame_count/(time.time() - t_start)
	# print "frame rate: %.1f"%frame_rate
	try:
		process = pool.apply_async( get_face_send, (image,) ) 
	 	process.get()		
		# cv2.imshow("Frame", image)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
		rawCapture.truncate( 0 )
	except:
		break

cv2.destroyAllWindows()

