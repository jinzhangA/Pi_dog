import pyaudio
import math
import socket
import pickle
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter
from scipy.signal import filtfilt
from matplotlib.mlab import find
from time import sleep
import time


CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
COMMAND_FREQ_HIGH = 800
COMMAND_FREQ_LOW = 300
STOP = 'stop'
GO = 'go'
PORT = 8089

def Pitch(input_signal):
	input_signal = np.fromstring(input_signal, 'Int16');
	crossing = [math.copysign(1.0, s) for s in input_signal]
	index = find(np.diff(crossing));
	f0=round(len(index) *RATE /(2*np.prod(len(input_signal))))
	return f0;

def UPD_send(command):
	message = pickle.dumps(('command', command))
	sock.sendto(message, ('localhost', PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
channels = CHANNELS,
rate = RATE,
input = True,
frames_per_buffer = CHUNK,
input_device_index = 0)

terminate_flag = False
last_sent_time = 0
check_hi = 0

while not terminate_flag :
	try:
		data = stream.read(CHUNK)
		frequency=Pitch(data)
		# print "%f Frequency" %frequency

		if check_hi > 0:
			if check_hi == 1:
				UPD_send(GO)
				last_sent_time = time.time()
				print "udp send go"

			elif frequency >= COMMAND_FREQ_HIGH:
				last_sent_time = time.time()
				UPD_send(STOP)
				check_hi = 1
				print "udp send STOP"
			check_hi -= 1

		elif frequency >= COMMAND_FREQ_HIGH and time.time() - last_sent_time >= 3:
			UPD_send(STOP)
			last_sent_time = time.time()
			print "udp send STOP"

		elif frequency >= COMMAND_FREQ_LOW and time.time() - last_sent_time >= 3:
			check_hi = 3

	except KeyboardInterrupt:
		exit()



