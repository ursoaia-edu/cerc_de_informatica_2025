
# import os
# import binascii
# import time
# import machine
# import pycom
# import struct
# from network import LoRa
#
# pycom.heartbeat(False)
# uart = machine.UART(0,115200)
# os.dupterm(uart)
# machine.main('main.py')
#
# lora = LoRa(mode=LoRa.LORAWAN)
#
# app_eui = binascii.unhexlify('70B3D57ED000F24B')
# app_key = binascii.unhexlify('2C9671F46F62907FC936E0E877CC4218')
#
# lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
# pycom.rgbled(0xffff00)
# while not lora.has_joined():
#     time.sleep(2.5)
#     print('Not joined yet...')
# print('Network joined!')
# pycom.rgbled(0x0000ff)
# time.sleep(1)
# pycom.rgbled(0x000000)

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
dev_addr = struct.unpack(">l", binascii.unhexlify('26011EE3'))[0]
nwk_swkey = binascii.unhexlify('6E1E5FEFF04617D5F5D0E915721D8C7F')
app_swkey = binascii.unhexlify('4987D94C81422EAAD5210BAB60F4228A')
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
pycom.rgbled(0xffff00)
while not lora.has_joined():
    time.sleep(2.5)
    print('Not joined yet...')
print('Network joined!')
pycom.rgbled(0x0000ff)
time.sleep(1)
pycom.rgbled(0x000000)
