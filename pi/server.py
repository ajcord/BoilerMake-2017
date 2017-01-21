from socket import *
from subprocess import call
from base64 import b64encode
import RPi.GPIO as GPIO
from motor import Motor

GPIO.setmode(GPIO.BOARD)
motors = [Motor([3,5,7,8]), Motor([11,13,15,16]), Motor([19,21,23,24])]
for m in motors:
    m.rpm = 1

def take_screenshot():
    print("taking screenshot")
    call(["raspistill", "-o", "capture.jpg", "-w", "320", "-h", "240", "-n", "-t", "1"])
    with open("capture.jpg", "r") as f:
        return b64encode(f.read())

def move_motor(which_motor, dest_angle):
    motors[which_motor].move_to(dest_angle)
    return "done"

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(("cardshark.local", 8000))
sock.listen(5)
while True:
    (client, address) = sock.accept()
    print("Accepted client")
    response = ""
    try:
        while True:
            client.sendall(response + "\r\n")
            query = client.recv(64)
            if query.endswith("\r\n"):
                query = query[:-2]
            else:
                response = "parse error"
                continue

            parsed = query.split(",")
            if query == "img":
                response = take_screenshot()
            elif len(parsed) == 3 and parsed[0] == "motor":
                which_motor = int(parsed[1])
                dest_angle = int(parsed[2])
                response = move_motor(which_motor, dest_angle)
            else:
                response = "parse error"
    except IOError:
        continue