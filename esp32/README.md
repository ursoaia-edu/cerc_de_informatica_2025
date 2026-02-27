# Cerc de Informatica 2025

A collection of ESP32 MicroPython projects built for the 2025 computer science circle.

## Projects

### [`led_blink`](led_blink/)

Blinks the ESP32's built-in LED (GPIO 2) on and off every second. The classic "Hello, World!" of embedded systems. Includes notes on connecting external LEDs and building a multi-LED chaser.

### [`themperature_and_humidity`](themperature_and_humidity/)

Reads temperature and humidity from a DHT22 (or DHT11) sensor on GPIO 14 and prints the values to the serial console every 2 seconds.

### [`themperature_and_humidity_web`](themperature_and_humidity_web/)

Extends the sensor project with a simple HTTP web server. After connecting to Wi-Fi, the ESP32 serves a styled HTML page showing live temperature and humidity readings. Navigate to the device's IP address in any browser to view them.

## Prerequisites

All projects require:

- ESP32 board with MicroPython firmware installed
- [Thonny IDE](https://thonny.org/) or a tool such as `mpremote` or `ampy`

### Flashing MicroPython

1. Download the latest firmware from [micropython.org](https://micropython.org/download/esp32/)
2. Flash it with `esptool`:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
   ```
## Reference

[LAFVIN Basic Starter Kit For Esp32 S3](https://basic-starter-kit-for-esp32-s3-wroom.readthedocs.io/en/latest/index.html)

[LAFVIN Super Starter Kit For Esp32 S3](https://super-starter-kit-for-esp32-s3-wroom.readthedocs.io/en/latest/index.html)

[ESP32 IOT Learning Kit](https://esp32-iot-learning-kit1.readthedocs.io/en/latest/)
