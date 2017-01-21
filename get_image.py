from socket import *
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(("cardshark.local", 8000))
sock.sendall("img\r\n")
time.sleep(1)
ret = sock.recv(1048576)
print(ret)
