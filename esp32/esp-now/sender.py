import network
import espnow
from esp import espnow

# Enable Wi-Fi
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Initialize ESP-NOW
e = espnow.ESPNow()
e.active(True)

# MAC address of receiver (replace with your receiver's MAC)
peer = b'\xaa\xbb\xcc\xdd\xee\xff'
e.add_peer(peer)

# Send message
e.send(peer, "Hello from Python!")