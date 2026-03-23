import socket
import pycom
from time import sleep


s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
temp = 0
while True:
    s.setblocking(True)
    s.send(bytes([0x01, 0x67, 0x00, 0x96]))
    s.setblocking(False)
    time.sleep(2.5)
    data = s.recv(64)
    print(str(temp) + ") ",end="")
    print(data)
    temp+=1
