import asyncio
import binascii
import os

import adafruit_displayio_ssd1306
import board
import displayio
import microcontroller
import terminalio
import wifi
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_sht31d import SHT31D

from adafruit_display_text import label

# Setup WiFi network
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to {} ...".format(secrets["ssid"]))
wifi.radio.connect(secrets["ssid"], secrets["password"])

# Get details about the filesystem
fs_stat = os.statvfs("/")

# Collect details about the system
details = {
    "machine": os.uname().machine,
    "mac": binascii.hexlify(wifi.radio.mac_address).decode(),
    "hostname": wifi.radio.hostname,
    "ip_address": wifi.radio.ipv4_address,
    "disk": fs_stat[0] * fs_stat[2] / 1024 / 1024,
    "free": fs_stat[0] * fs_stat[3] / 1024 / 1024,
    "ssid": wifi.radio.ap_info.ssid,
    "channel": wifi.radio.ap_info.channel,
}

# Setup I2C
i2c = board.I2C()

# Setup the M5Stack Env. sensor II
bmp280 = Adafruit_BMP280_I2C(i2c, address=0x76)
sht30 = SHT31D(i2c)

bmp280.sea_level_pressure = 1013.25

# Setup display
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=board.LCD_RST)

WIDTH = 128
HEIGHT = 32
BORDER = 1

display = adafruit_displayio_ssd1306.SSD1306(
    display_bus, width=WIDTH, height=HEIGHT, rotation=180
)

# Create a group
group = displayio.Group()
display.show(group)

# Set text, font and color for the label
font = terminalio.FONT  # Standard font
color = 0xFFFFFF  # White

# Create the sensor label
sensor0_text = "Temperature:"
sensor0_label0 = label.Label(font, text=sensor0_text, color=color, x=4, y=10 - 1)
group.append(sensor0_label0)

# Create label for the sensor value
sensor0_value = "0"
sensor0_label1 = label.Label(font, text=sensor0_value, color=color, x=80, y=10 - 1)
group.append(sensor0_label1)

sensor1_text = "Humidity:"
sensor1_label0 = label.Label(font, text=sensor1_text, color=color, x=4, y=20 - 1)
group.append(sensor1_label0)

# Create label for the sensor value
sensor1_value = "0"
sensor1_label1 = label.Label(font, text=sensor1_value, color=color, x=80, y=20 - 1)
group.append(sensor1_label1)


async def print_serial_data(content, title=None):
    """Print details on startup to serial."""
    if title is not None:
        print("{}".format(title))
        print("=" * len(title))
    for title, data in content.items():
        print("{}: {}".format(title, data))
    print("")
    await asyncio.sleep(1)


async def update_display_value():
    """Update the value to display."""
    while True:
        sensor0_label1.text = "{:.1f}".format(
            (sht30.temperature + bmp280.temperature) / 2
        )
        sensor1_label1.text = "{:.1f}".format(sht30.relative_humidity)
        await asyncio.sleep(5)


async def update_sensor_values():
    """Update the value to serial."""
    while True:
        sensor_data = {
            "temperature": "{} C".format((sht30.temperature + bmp280.temperature) / 2),
            "humidity": "{} %".format(sht30.relative_humidity),
            "pressure": "{} C".format(bmp280.pressure),
            "altitude": "{} C".format(bmp280.altitude),
            "cpu_temperature": "{} C".format(microcontroller.cpu.temperature),
        }
        await print_serial_data(sensor_data)
        await asyncio.sleep(5)


async def main():
    """Main part."""
    startup = asyncio.create_task(print_serial_data(details, "System details"))
    display_task = asyncio.create_task(update_display_value())
    serial_task = asyncio.create_task(update_sensor_values())

    await asyncio.gather(startup, display_task, serial_task)


asyncio.run(main())
