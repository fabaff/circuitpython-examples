# Seeeduino XIAO (SAMD21 Cortex® M0+)
# 
# Hardware: https://www.seeedstudio.com/Seeeduino-XIAO-Arduino-Microcontroller-SAMD21-Cortex-M0+-p-4426.html
# CircuitPython: https://circuitpython.org/board/seeeduino_xiao/
#
# Reset: RST pads short-cut two times
#

import os

import microcontroller
import board
import time
from digitalio import DigitalInOut, Direction, Pull

# Get details about the filesystem
fs_stat = os.statvfs("/")

# Collect details about the system
details = {
    "machine": os.uname().machine,
    "disk": fs_stat[0] * fs_stat[2] / 1024 / 1024,
    "free": fs_stat[0] * fs_stat[3] / 1024 / 1024,
}

# Print details about the available pins
# See https://learn.adafruit.com/circuitpython-essentials/circuitpython-pins-and-modules#what-are-all-the-available-names-3082670-19
def show_pin_details():
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

def show_details_startup(title, content):
    """Print details on startup to serial."""
    print("")
    print("{}".format(title))
    print("=" * len(title))
    for title, data in content.items():
        print("{}: {}".format(title, data))
    # or simpler
    # [print(key,':',value) for key, value in content.items()]
    print("")

# Set up the LED
led = DigitalInOut(board.BLUE_LED)
led.direction = Direction.OUTPUT

# Print the details
show_details_startup("System details", details)
show_pin_details()

print("Blink LED in a endless loop ...")
while True:
    led.value = False
    time.sleep(1)
    led.value = True
    time.sleep(1)
