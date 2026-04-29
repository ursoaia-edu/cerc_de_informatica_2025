import network
import espnow
from esp import espnow

# Enable Wi-Fi
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Initialize ESP-NOW
e = espnow.ESPNow()
e.active(True)

while True:
    host, msg = e.recv()
    if msg:
        print(msg)