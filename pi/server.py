from socket import *
from subprocess import call
from base64 import b64encode
import RPi.GPIO as GPIO
from motor import Motor
import subprocess

suction_pin = 26

GPIO.setmode(GPIO.BOARD)
GPIO.setup(suction_pin, GPIO.OUT)
motors = [Motor([3,5,7,12]), Motor([11,13,15,16]), Motor([19,21,23,24])]
for m in motors:
    m.rpm = 5

def take_screenshot():
    print("taking screenshot")
    call(["raspistill", "-o", "capture.jpg", "-w", "320", "-h", "240", "-n", "-t", "1"])
    with open("capture.jpg", "r") as f:
        return b64encode(f.read())

def move_motor(which_motor, dest_angle):
    motors[which_motor].move_to(dest_angle)
    return "done"

def toggle_suction(enable):
    GPIO.output(suction_pin, enable)
    return "done"

def reply(uart, response):
    uart.write(str(response) + "\n")

with open("/dev/ttyAMA0", "r+w") as uart:
    subprocess.call(["stty", "-F", "/dev/ttyAMA0", "115200"])
    while True:
        query = uart.readline()
        if query.endswith("\n"):
            query = query[:-1]
        else:
            reply(uart, "parse error")
            continue

        parsed = query.split(",")
        if query == "img":
            take_screenshot()
            reply(uart, "capture.jpg")
        elif len(parsed) == 3 and parsed[0] == "motor":
            which_motor = int(parsed[1])
            dest_angle = int(parsed[2])
            reply(uart, move_motor(which_motor, dest_angle))
        elif len(parsed) == 2 and parsed[0] == "suction":
            enable = int(parsed[1])
            reply(uart, toggle_suction(enable))
        else:
            reply(uart, "parse error")
