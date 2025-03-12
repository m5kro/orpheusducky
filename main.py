from machine import Pin, PWM
from keystrokes import interpret_ducky_script
import time
import neopixel

# Set up button on GPIO 25
button = Pin(25, Pin.IN, Pin.PULL_UP)

# Short delay for button state stabilization.
time.sleep(0.1)

# Status light
pwm_led = PWM(Pin(23))
pwm_led.freq(1000)
pwm_led.duty_u16(65535 // 8)

# RGB LED
np = neopixel.NeoPixel(Pin(24), 1)

# With a pull-up, the button value is 1 when not pressed and 0 when pressed.
if button.value() == 0:
    print("Button pressed. Skipping Rubber Ducky script execution.")

    # Set RGB led to purple/pink
    np[0] = (32, 0, 32)
    np.write()
else:
    print("Button not pressed. Executing Rubber Ducky script.")
    
    # Set to blue
    np[0] = (0, 0, 64)
    np.write()
    interpret_ducky_script("DuckyScript.txt")

pwm_led.duty_u16(0)