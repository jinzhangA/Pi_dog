import RPi.GPIO as GPIO
from motor_control_pigpio import pwm_motor
from datetime import datetime
from wheel import Wheel
import socket
import pickle
import time
import pygame
import thread


class Dog():
	def __init__ (self, left_channel, right_channel):
		self.left_wheel = Wheel('left', left_channel)
		self.right_wheel = Wheel('right', right_channel)

	def move(self, error):
		x_error, y_error = error
		if not x_error and not y_error:
			global last_move_instruction
			if last_move_instruction != 0:
				self.left_wheel.forward(0);
				self.right_wheel.forward(0);
				last_move_instruction = 0
			return

		y = int(y_error/2)

		if x_error >= 80:
			x = 2
		elif x_error <= -80:
			x = -2
		elif x_error >= 40:
			x = 1
		elif x_error <= -40:
			x = -1
		elif x_error < 40 or x_error > -40:
			x = 0

		if x != 0 or y != 0:
			left = self.clamp(-x+y)
			right = self.clamp(x+y)

			self.left_wheel.forward(left);
			self.right_wheel.forward(right);
			last_move_instruction = 1
		else:
			self.left_wheel.forward(0);
			self.right_wheel.forward(0);
			last_move_instruction = 0

	@staticmethod
	def clamp(in_put, uppper_bound = 10, lower_bound = -10):
		if in_put < lower_bound:
			in_put = lower_bound
		elif in_put > uppper_bound:
			in_put = uppper_bound
		return in_put

	@staticmethod
	def bark(index):
		if index == 'stop':
			pygame.mixer.music.load("sounds/dog_puppy.wav")
		if index == 'missing_face':
			pygame.mixer.music.load("sounds/dog_whine_duke.wav")
		if index == 'go':
			pygame.mixer.music.load("sounds/dog_bark4.wav")
		pygame.mixer.music.play()


if __name__ == '__main__':
	LEFT_CHANNEL = 20
	RIGHT_CHANNEL = 21
	GPIO.setmode(GPIO.BCM)
	dog = Dog(LEFT_CHANNEL, RIGHT_CHANNEL)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.bind(('localhost', 8089))

	pygame.mixer.init()
	move = False
	continue_loop = True
	found_face = True
	last_bark = 0
	last_move_instruction = None
	while continue_loop:
		try:
			data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
			data = pickle.loads(data)
			if data[0] == 'error':
				if data[1] == (None, None):
					dog.move( (0, 0) )
					if found_face == True:
						found_face = False
						if time.time() - last_bark >= 3:
							dog.bark('missing_face')
							last_bark = time.time()

				elif move:
					found_face = True
					dog.move(data[1])
				elif not move:
					found_face = True
					dog.move( (0, 0) )

			if data[0] == 'command':
				print data[1]
				if data[1] == 'stop':
					move = False
					dog.bark('stop')
				else:
					move = True
					dog.bark('go')
		except KeyboardInterrupt:
			dog.move( (0, 0) )
			continue_loop = False




