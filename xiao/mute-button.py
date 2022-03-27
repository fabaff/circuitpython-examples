"""Button which sends one key combination."""
import time
import board

from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import usb_hid

# Define output LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# Configure as keyboard
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# Define button
button = DigitalInOut(board.D10)
button.direction = Direction.INPUT
button.pull = Pull.UP

is_led_on = False
is_button_ready = True

while True:
    if is_button_ready and button.value is False:  # Button pressed
        is_button_ready = False
        if not is_led_on:
            print("Mute Microsoft Teams ...")
            kbd.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.M)
            is_led_on = True
            led.value = True
        else:
            print("Unmute Microsoft Teams ...")
            kbd.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.M)
            is_led_on = False
            led.value = False
    if button.value is True:  # Button released
        is_button_ready = True
    time.sleep(0.05)
