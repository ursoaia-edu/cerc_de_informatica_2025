import os
import binascii
import time
import machine
import pycom
import struct
from network import LoRa
pycom.heartbeat(False)
uart = machine.UART(0,115200)
os.dupterm(uart)
machine.main('main.py')
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
dev_addr = struct.unpack(">l", binascii.unhexlify('26011346'))[0]
nwk_swkey = binascii.unhexlify('0619AB7D261950743D46D701AD9903DD')
app_swkey = binascii.unhexlify('8FBE002AA5008BCC52638CF2D33A6A10')
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
pycom.rgbled(0xffff00)
while not lora.has_joined():
    time.sleep(2.5)
    print('Not joined yet...')
print('Network joined!')
pycom.rgbled(0x0000ff)
time.sleep(1)
pycom.rgbled(0x000000)
