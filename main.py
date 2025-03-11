# Litraly repurposed from sprig spear's code
from machine import Pin
from keystrokes import interpret_ducky_script
import time

# Set up button on GPIO 25
button = Pin(25, Pin.IN, Pin.PULL_UP)

# Short delay for button state stabilization.
time.sleep(0.1)

# With a pull-up, the button value is 1 when not pressed and 0 when pressed.
if button.value() == 0:
    print("Button pressed. Skipping Rubber Ducky script execution.")
else:
    print("Button not pressed. Executing Rubber Ducky script.")
    interpret_ducky_script("DuckyScript.txt")