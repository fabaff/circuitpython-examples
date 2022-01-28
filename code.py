# WEMOS S2 Pico
# https://www.wemos.cc/en/latest/s2/s2_pico.html
#

import asyncio
import os
import time

import adafruit_displayio_ssd1306
import board
import countio
import digitalio
import displayio
import microcontroller
import terminalio
import wifi
from adafruit_display_text import label
from digitalio import DigitalInOut, Direction, Pull

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
    "mac": wifi.radio.mac_address,
    "hostname": wifi.radio.hostname,
    "ip_address": wifi.radio.ipv4_address,
    "disk": fs_stat[0] * fs_stat[2] / 1024 / 1024,
    "free": fs_stat[0] * fs_stat[3] / 1024 / 1024,
    "ssid": wifi.radio.ap_info.ssid,
    "channel": wifi.radio.ap_info.channel,
}

# Setup display
displayio.release_displays()

i2c = board.I2C()
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

# Set text, font, and color for the label
font = terminalio.FONT  # Standard font
color = 0xFFFFFF  #  White

# Create the sensor label
sensor_text = "CPU Temp.:"
sensor_label0 = label.Label(font, text=sensor_text, color=color, x=4, y=HEIGHT // 2 - 1)
group.append(sensor_label0)

# Create label for the sensor value
sensor_value = "not avail."
sensor_label1 = label.Label(
    font, text=sensor_value, color=color, x=72, y=HEIGHT // 2 - 1
)
group.append(sensor_label1)

# Print details about the available pins
# See https://learn.adafruit.com/circuitpython-essentials/circuitpython-pins-and-modules#what-are-all-the-available-names-3082670-19
async def show_pin_details():
    """Show pin overview."""
    print("")
    print("Pin details")
    print("===========")
    board_pins = []
    for pin in dir(microcontroller.pin):
        if isinstance(getattr(microcontroller.pin, pin), microcontroller.Pin):
            pins = []
            for alias in dir(board):
                if getattr(board, alias) is getattr(microcontroller.pin, pin):
                    pins.append("board.{}".format(alias))
            if len(pins) > 0:
                board_pins.append(" ".join(pins))
    for pins in sorted(board_pins):
        print(pins)
    print("")
    await asyncio.sleep(1)


async def show_details_startup(title, content):
    """Print details on startup to serial."""
    print("")
    print("{}".format(title))
    print("=" * len(title))
    for title, data in content.items():
        print("{}: {}".format(title, data))
    # or simpler
    # [print(key,':',value) for key, value in content.items()]
    print("")
    await asyncio.sleep(1)


async def catch_interrupt(pin):
    """Print a message when button is pressed and released."""
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                interrupt.count = 0
                print("Button on {} pressed".format(pin))
            await asyncio.sleep(0)


async def blink_forever(pin, interval):
    """Blink LED with given interval."""
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        while True:
            led.value = True
            await asyncio.sleep(interval)
            led.value = False
            await asyncio.sleep(interval)


async def blink(pin, interval, count):
    """Blink LED with given interval and count."""
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            led.value = True
            await asyncio.sleep(interval)
            led.value = False
            await asyncio.sleep(interval)


async def update_display_value():
    """Update the value to display."""
    while True:
        sensor_label1.text = "{:.1f}".format(microcontroller.cpu.temperature)
        await asyncio.sleep(5)


async def main():
    """Main part."""
    startup = asyncio.create_task(show_details_startup("System details", details))
    pins = asyncio.create_task(show_pin_details())
    led1_task = asyncio.create_task(blink_forever(board.IO10, 0.5))
    led2_task = asyncio.create_task(blink(board.IO11, 0.5, 10))

    display_task = update_display_value()

    interrupt_task = asyncio.create_task(catch_interrupt(board.BUTTON))

    await asyncio.gather(
        startup, pins, led1_task, led2_task, display_task, interrupt_task
    )


asyncio.run(main())
