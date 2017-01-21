from socket import *
from subprocess import call
from base64 import b64encode

def take_screenshot():
    print("taking screenshot")
    call(["raspistill", "-o", "capture.jpg", "-w", "320", "-h", "240", "-n", "-t", "1"])
    with open("capture.jpg", "r") as f:
        return b64encode(f.read())

def move_motor(which_motor, num_steps):
    # TODO
    return "done"

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(("localhost", 8000))
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
                which_motor = parsed[1]
                num_steps = parsed[2]
                response = move_motor(which_motor, num_steps)
            else:
                response = "parse error"
    except IOError:
        continue