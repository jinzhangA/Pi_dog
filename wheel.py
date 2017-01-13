import RPi.GPIO as GPIO
from motor_control_pigpio import pwm_motor
from datetime import datetime

class Wheel():
	def __init__ (self, left_right, channel):
		if left_right == 'left':
			self.left_right = 'left'
		else:
			self.left_right = 'right'

		self.channel = channel
		self.state = "stop"
		self.speed = 0
		self.motor = pwm_motor(channel = self.channel)

	def forward(self, speed = 5):
		if self.left_right == 'left':
			self.motor.change_speed(speed)
		else:
			self.motor.change_speed(-speed)
		self.state = "forward"
		self.speed = speed

	def backward(self, speed = 5):
		if self.left_right == 'left':
			self.motor.change_speed(-speed)
		else:
			self.motor.change_speed(speed)
		self.state = "backward"
		self.speed = speed

	def stop(self):
		self.motor.change_speed(0)
		self.state = "stop"
		self.speed = 0

	def get_state(self, print_it = False):
		the_time = datetime.now().strftime('%H:%M:%S')
		status = "%s: %s %s %d"%(the_time, self.left_right, self.state, self.speed)
		if print_it:
			print status
		return status

	def terminate(self):
		self.motor.stop_motor()