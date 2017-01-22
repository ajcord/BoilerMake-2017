from socket import *
from subprocess import call
from base64 import b64encode
import RPi.GPIO as GPIO
from motor import Motor

suction_pin = 26

GPIO.setmode(GPIO.BOARD)
GPIO.setup(suction_pin, GPIO.OUT)
motors = [Motor([3,5,7,8]), Motor([11,13,15,16]), Motor([19,21,23,24])]
for m in motors:
    m.rpm = 5

def take_screenshot():
    print("taking screenshot")
    call(["raspistill", "-o", "capture.jpg", "-w", "320", "-h", "240", "-n", "-t", "1"])
    with open("capture.jpg", "r") as f:
        return b64encode(f.read())

def move_motor(which_motor, dest_angle):
    m = motors[which_motor]
    # curr_angle = m.curr_angle
    # if abs(dest_angle - curr_angle) >= 180:
    #     if dest_angle > curr_angle:
    #         int_angle = dest_angle - 179
    #     else:
    #         int_angle = dest_angle + 179
    #     m.move_to(int_angle)
    #     move_motor(which_motor, dest_angle)
    # else:
    m.move_to(dest_angle)
    return "done"

def toggle_suction(enable):
    GPIO.output(suction_pin, enable)
    return "done"

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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
            elif len(parsed) == 2 and parsed[0] == "suction":
                enable = int(parsed[1])
                response = toggle_suction(enable)
            else:
                response = "parse error"
    except IOError:
        continue