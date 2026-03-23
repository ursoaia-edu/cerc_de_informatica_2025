import socket
import pycom
from time import sleep
from pysense import Pysense
from SI7006A20 import SI7006A20

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

s.bind(2)


py = Pysense()
si = SI7006A20(py)
print("lel")
while True:
    s.setblocking(True)
    h = (str(si.humidity())).split('.')
    print(h)
    s.send(bytes([int(h[0]), int(h[1][:2])]))

    s.setblocking(False)
    sleep(1)
    command = s.recv(64)
    print(command)
    if command == b'\x01':
        pycom.rgbled(0xff0000)
    elif command == b'\x02':
        pycom.rgbled(0x00ff00)
    sleep(5)
    del h, command
    pycom.rgbled(0x000000)

s.setblocking(False)
