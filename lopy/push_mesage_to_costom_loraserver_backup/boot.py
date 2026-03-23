
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

lora = LoRa(mode=LoRa.LORAWAN)

app_eui = binascii.unhexlify('70B3D57ED000B1DB')
app_key = binascii.unhexlify('7530DF0EBEE4F03D93F95B0D8B17D9EC')

lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
pycom.rgbled(0xffff00)
while not lora.has_joined():
    time.sleep(2.5)
    print('Not joined yet...')
print('Network joined!')
pycom.rgbled(0x0000ff)
time.sleep(1)
pycom.rgbled(0x000000)
