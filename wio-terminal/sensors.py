# Example for the built-in sensors
import board
import terminalio
import time
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
import microcontroller
import displayio
import adafruit_lis3dh
from adafruit_simple_text_display import SimpleTextDisplay
import busio
from adafruit_display_text import label


i2c_gyro = busio.I2C(board.GYROSCOPE_SCL, board.GYROSCOPE_SDA)

int1 = DigitalInOut(board.GYROSCOPE_INT)

lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c_gyro, address=0x18, int1=int1)

analog_in = AnalogIn(board.LIGHT) # Light Sensor pin on Wio Terminal

display = board.DISPLAY

text = "Hello world"
text_area = label.Label(terminalio.FONT, text=text)
text_area.x = 100
text_area.y = 100
board.DISPLAY.show(text_area)


def get_voltage(pin):
    return (pin.value * 3.3) / 65536
 
temperature_data = SimpleTextDisplay(title="Sensor Data", title_scale=2)

while True:
    x, y, z = lis3dh.acceleration
    print("Light Sensor Voltage:", get_voltage(analog_in))
    print(f"CPU: {microcontroller.cpu.temperature}")
    time.sleep(2)
    temperature_data[0].text = "CPU Temperature: {:.2f} C".format(microcontroller.cpu.temperature)
    temperature_data[1].text = "Light: {:.2f} V".format(get_voltage(analog_in))
    temperature_data[2].text = "X: {:.2f} m/s^2".format(x)
    temperature_data[3].text = "Y: {:.2f} m/s^2".format(y)
    temperature_data[4].text = "Z: {:.2f} m/s^2".format(z)

    temperature_data.show()
