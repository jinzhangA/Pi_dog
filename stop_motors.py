from motor_control_pigpio import pwm_motor
import RPi.GPIO as GPIO
import pigpio

GPIO.setmode(GPIO.BCM)
motor_1 = pwm_motor(20)
motor_2 = pwm_motor(21)
motor_1.change_speed(0)
motor_2.change_speed(0)

