# Temperature and Humidity

Reads temperature and humidity from a DHT22 (or DHT11) sensor connected to an ESP32 and prints the values to the serial console every 2 seconds using MicroPython.

## Description

This script uses the built-in `dht` MicroPython library to communicate with a DHT22 sensor over a single data pin (GPIO 14). It reads the temperature in Celsius, converts it to Fahrenheit, and reads the relative humidity, printing all three values in a loop. If the sensor fails to respond, an error message is printed instead of crashing.

## Wiring

### DHT22 (or DHT11) to ESP32

```
DHT22 Pin  →  ESP32
---------     -----
VCC (1)    →  3.3V
DATA (2)   →  GPIO 14
GND (4)    →  GND
```

A 10 kΩ pull-up resistor between DATA and VCC is recommended for reliable communication.

```
3.3V ──[10kΩ]──┬── GPIO 14
               │
              DATA pin of sensor
```

> **DHT11 vs DHT22:** The DHT11 has lower accuracy (±2°C, ±5% RH) and a narrower range. The DHT22 is more precise (±0.5°C, ±2–5% RH) and supports a wider temperature range. To use a DHT11, comment out the DHT22 line and uncomment the DHT11 line in `main.py`.

### Wiring Diagram

![ESP32 dht11](../../images/ESP32-interfacing-with-dht11.webp)

![ESP32 dht22 wifi](../../images/016-esp32-micropython-wifi-ap-techtotinker-diagram.png)

![ESP32 dht22](../../images/esp32-micropython-dht22-temperature-humidity-sensor-wiring-diagram.jpg)

---

## Getting Started

### Prerequisites

- ESP32 board with MicroPython firmware installed
- DHT22 or DHT11 sensor
- [Thonny IDE](https://thonny.org/) or a tool such as `mpremote` or `ampy`

### Flashing MicroPython (if not already installed)

1. Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)
2. Flash it using `esptool`:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
   ```

### Running the Script

**Using Thonny:**
1. Connect your ESP32 via USB and open Thonny
2. Open `main.py` and click **Run**, or save it as `main.py` on the device to run on boot
3. Open the serial monitor to see the output

**Using mpremote:**
```bash
mpremote connect /dev/ttyUSB0 run main.py
```

**Using ampy:**
```bash
ampy --port /dev/ttyUSB0 run main.py
```

### Expected Output

```
Temperature: 23.5 C
Temperature: 74.3 F
Humidity: 55.0 %
```

Values are printed every 2 seconds. If the sensor is not connected or fails to respond, you will see:

```
Failed to read sensor.
```

** References

[ESP32 Based Webserver for Temperature and Humidity Measurement using DHT11 Sensor](https://circuitdigest.com/microcontroller-projects/esp32-webserver-for-temperature-and-humidity-measurement-using-dht11-sensor)

[ESP32 MicroPython DHT22 Temperature Humidity Sensor](https://newbiely.com/tutorials/esp32-micropython/esp32-micropython-dht22-temperature-humidity-sensor)
