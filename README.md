# Orpheus Ducky
Turn your Orpheus pico into a rubber ducky! (or any regular pico too)

# Install
1. Aquire an Orpheus pico or a Raspberry pi pico
2. [Download the micropython firmware](https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2)
3. Flash the firmware
4. Use [Thonny](https://thonny.org/) or [MicroPico](https://github.com/paulober/MicroPico) to send all the python files to the Pico
5. Create a DuckyScript.txt and place it in the Pico (or copy the one in this repo as an example)
6. Install mpremote using pip `python3 -m pip install mpremote` (linux users may need to install via their package manager)
7. Install keyboard libraries `python3 -m mpremote mip install usb-device-keyboard usb-device-mouse neopixel`, you may need to close vscode or thonny during this part
8. Unplug and replug the pico

# Usage
You may use most of the available functions of [duckyscript 3.0](https://docs.hak5.org/hak5-usb-rubber-ducky/duckyscript-quick-reference/) in your script.

## Mouse
Since Duckyscript 3.0 does not have any mouse commands, I have created some.<br>
**Warning:** Mouse support is still very buggy, there is also a delay when initializing the mouse, so it is recommened to use the mouse block for multiple continuous actions.
| Command | Usage |
| ------- | ----- |
| `MOUSE` | Start of a mouse block |
| `END_MOUSE` | End of a mouse block |
| `MOUSE_MOVE` x y | Move the mouse by x and y amount |
| `MOUSE_LEFT_CLICK` | Left click |
| `MOUSE_RIGHT_CLICK` | Right click |
| `MOUSE_MIDDLE_CLICK` | Middle click |

## What's Not Working
1. Different key layouts
2. Hardware ID values (maybe)
3. WAIT_FOR ([possible with led updates](https://github.com/micropython/micropython-lib/blob/fbf7e120c6830d8d04097309e715bcab63dcca67/micropython/usb/usb-device-keyboard/usb/device/keyboard.py))
4. SAVE and RESTORE (need a way to get the state)
5. Exfiltration (never gonna work)
6. OS detection (possible but difficult)

## Other Notes
If you are using an Orpheus pico you may hold down the auxilliary button (button on GPIO 25) to prevent script execution or stop a currently running script.<br>
<br>
You may also need to increase the delay on line 193 in keystrokes if the keyboard isn't being initialized in time.

# RGB Led Status Colors
 
- Blue — no errors, running fine
- Red — error occured while running script
- Yellow — stopped script execution (from holding button during script execution)
- Pink — skipped script execution (from holding the button while plugging in)
<br>
The green status light will also be on during script executition. The pico will attempt to continue executing the script even if there is an error.

# TODO
1. Add support for non working parts of duckyscript

# License
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)<br>
Attribution-NonCommercial-ShareAlike 4.0 International <br>
<br>
**You are free to:**
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material
<br>

**Under the following terms:**
<br>
- Attribution — You must give [appropriate credit](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en#ref-appropriate-credit) , provide a link to the license, and [indicate if changes were made](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en#ref-indicate-changes). You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. 
- NonCommercial — You may not use the material for [commercial purposes](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en#ref-commercial-purposes). 
- ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the [same license](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en#ref-same-license) as the original.
