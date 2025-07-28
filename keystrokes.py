# m5kro - 2025
# A jank implementation of a DuckyScript 3.0 interpreter
# The code is quacking at me ... Please send help ╥﹏╥

# TODO:
# - Add support for mouse movements and clicks
# - Add support for WAIT_FOR command (maybe)
# - Figure out a way to get the capslock, numlock, and fnlock status

import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode
from usb.device.mouse import MouseInterface
import time
import random
from machine import Pin, soft_reset, PWM
import neopixel

# Dummy keyboard class for testing purposes
"""
class DummyKeyboard:
    def __getattr__(self, name):
        # Return a dummy function that does nothing
        def dummy_function(*args, **kwargs):
            # Optionally, log the call for debugging:
            # print(f"Called {name} with args: {args} kwargs: {kwargs}")
            pass
        return dummy_function

keyboard = DummyKeyboard()
"""

# Actual keyboard class, comment out to debug using the dummy keyboard

# Initialize the keyboard interface only when running as a script.
keyboard = KeyboardInterface()
mouse = MouseInterface()
usb.device.get().init(keyboard, builtin_driver=True)

# Various variables
rem_block = False  # Flag to ignore REM_BLOCK sections
string_block = False  # Flag for STRING BLOCK sections
stringln_block = False  # Flag for STRINGLN BLOCK sections
mouse_block = False  # Flag for MOUSE BLOCK sections
constants = {}  # Dictionary to store constants
variables = {}  # Dictionary to store variables
functions = {}  # Dictionary to store functions
held_keys = []  # List to store currently held keys
if_else_conditions = []  # List to store if-else conditions
if_else_blocks = []  # List to store if-else blocks
current_if_else = 0  # Index of the current if-else block
num_if_else = 0  # Number of if-else blocks
reading_if_else = False  # Flag to indicate if we are reading an if-else block
reading_while = False  # Flag to indicate if we are reading a while loop
reading_function = False  # Flag to indicate if we are reading a function
current_function = ""  # String to store the current function name
num_whiles = 0  # Number of while loops
while_condition = ""  # String to store the while condition
while_block = ""  # String to store the while block
jitter = False  # Flag to indicate if we should add jitter
max_jitter = 20  # Maximum jitter in milliseconds to add to the keypress delay
random_min = 0  # Minimum random value for number generation
random_max = 65535  # Maximum random value for number generation

keypress_delay = 0.0  # Delay in seconds between keypresses, supports decimal values

# Define the button to stop
button_left = Pin(25, Pin.IN, Pin.PULL_UP)

# Set up the RGB LED on GPIO 24
np = neopixel.NeoPixel(Pin(24), 1)

# Green led on GPIO 23
pwm_led = PWM(Pin(23))

# Modifier keys dictionary
MODIFIER_KEYS = {
    'CTRL': KeyCode.LEFT_CTRL,
    'CONTROL': KeyCode.LEFT_CTRL,
    'SHIFT': KeyCode.LEFT_SHIFT,
    'ALT': KeyCode.LEFT_ALT,
    'GUI': KeyCode.LEFT_UI,  # Commonly represents the Windows or Command key
    'COMMAND': KeyCode.LEFT_UI,  # Same as GUI
    'WINDOWS': KeyCode.LEFT_UI  # Same as GUI
}

# Special keys dictionary
SPECIAL_KEYS = {
    'ENTER': KeyCode.ENTER,
    'INSERT': KeyCode.INSERT,
    'DELETE': KeyCode.DELETE,
    'DEL': KeyCode.DELETE,
    'ESCAPE': KeyCode.ESCAPE,
    'UP': KeyCode.UP,
    'UPARROW': KeyCode.UP,
    'DOWN': KeyCode.DOWN,
    'DOWNARROW': KeyCode.DOWN,
    'LEFT': KeyCode.LEFT,
    'LEFTARROW': KeyCode.LEFT,
    'RIGHT': KeyCode.RIGHT,
    'RIGHTARROW': KeyCode.RIGHT,
    'BACKSPACE': KeyCode.BACKSPACE,
    'SPACE': KeyCode.SPACE,
    'TAB': KeyCode.TAB,
    'CAPSLOCK': KeyCode.CAPS_LOCK,
    'NUMLOCK': KeyCode.KP_NUM_LOCK,
    'SCROLLLOCK': KeyCode.SCROLL_LOCK,
    'PRINTSCREEN': KeyCode.PRINTSCREEN,
    'PAGEUP': KeyCode.PAGEUP,
    'PAGEDOWN': KeyCode.PAGEDOWN,
    'HOME': KeyCode.HOME,
    'END': KeyCode.END,
    'F1': KeyCode.F1,
    'F2': KeyCode.F2,
    'F3': KeyCode.F3,
    'F4': KeyCode.F4,
    'F5': KeyCode.F5,
    'F6': KeyCode.F6,
    'F7': KeyCode.F7,
    'F8': KeyCode.F8,
    'F9': KeyCode.F9,
    'F10': KeyCode.F10,
    'F11': KeyCode.F11,
    'F12': KeyCode.F12
}

# Map characters to KeyCodes
CHARACTER_TO_KEYCODE = {
    'a': KeyCode.A, 'b': KeyCode.B, 'c': KeyCode.C, 'd': KeyCode.D, 'e': KeyCode.E,
    'f': KeyCode.F, 'g': KeyCode.G, 'h': KeyCode.H, 'i': KeyCode.I, 'j': KeyCode.J,
    'k': KeyCode.K, 'l': KeyCode.L, 'm': KeyCode.M, 'n': KeyCode.N, 'o': KeyCode.O,
    'p': KeyCode.P, 'q': KeyCode.Q, 'r': KeyCode.R, 's': KeyCode.S, 't': KeyCode.T,
    'u': KeyCode.U, 'v': KeyCode.V, 'w': KeyCode.W, 'x': KeyCode.X, 'y': KeyCode.Y,
    'z': KeyCode.Z, ' ': KeyCode.SPACE,
    '0': KeyCode.N0, '1': KeyCode.N1, '2': KeyCode.N2, '3': KeyCode.N3, '4': KeyCode.N4,
    '5': KeyCode.N5, '6': KeyCode.N6, '7': KeyCode.N7, '8': KeyCode.N8, '9': KeyCode.N9,
    '-': KeyCode.MINUS, '=': KeyCode.EQUAL, '[': KeyCode.OPEN_BRACKET, ']': KeyCode.CLOSE_BRACKET,
    '\\': KeyCode.BACKSLASH, ';': KeyCode.SEMICOLON, '\'': KeyCode.QUOTE, '`': KeyCode.GRAVE,
    ',': KeyCode.COMMA, '.': KeyCode.DOT, '/': KeyCode.SLASH, '\n': KeyCode.ENTER, '\t': KeyCode.TAB
}

# Special characters that require Shift modifier
SHIFT_REQUIRED_CHARACTERS = {
    '!': KeyCode.N1, '@': KeyCode.N2, '#': KeyCode.N3, '$': KeyCode.N4,
    '%': KeyCode.N5, '^': KeyCode.N6, '&': KeyCode.N7, '*': KeyCode.N8,
    '(': KeyCode.N9, ')': KeyCode.N0, '_': KeyCode.MINUS, '+': KeyCode.EQUAL,
    '{': KeyCode.OPEN_BRACKET, '}': KeyCode.CLOSE_BRACKET, '|': KeyCode.BACKSLASH,
    ':': KeyCode.SEMICOLON, '"': KeyCode.QUOTE, '<': KeyCode.COMMA, '>': KeyCode.DOT,
    '?': KeyCode.SLASH
}

def enable_mouse():
    # Enable the mouse interface
    try:
        usb.device.get().init(mouse, builtin_driver=True)
        time.sleep(1)  # Give some time for the mouse to initialize
        print("Mouse interface enabled.")
    except Exception as e:
        print(f"Failed to enable mouse interface: {e}")

def disable_mouse():
    # Disable the mouse interface by reinitializing the keyboard
    try:
        usb.device.get().init(keyboard, builtin_driver=True)
        time.sleep(1)  # Give some time for the keyboard to reinitialize
        print("Mouse interface disabled, keyboard reinitialized.")
    except Exception as e:
        print(f"Failed to disable mouse interface: {e}")

def send_string(text):
    global jitter, max_jitter, keypress_delay

    # Quit if left button held down
    if button_left.value() == 0:
        print("Stopping execution...")
        pwm_led.duty_u16(0)
        np[0] = (32, 32, 0)
        np.write()
        exit()

    # Send a string character by character
    for char in text:
        if char.islower() or char.isdigit() or char in CHARACTER_TO_KEYCODE:
            # Send lowercase letters, digits, and space
            keycode = CHARACTER_TO_KEYCODE[char.lower()]
            keyboard.send_keys([keycode])
            if jitter:
                time.sleep(random.randint(0, max_jitter) / 1000.0)
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release the key
            keyboard.send_keys(held_keys) # Keep held keys held
        elif char.isupper():
            # Send uppercase letters with Shift
            keycode = CHARACTER_TO_KEYCODE[char.lower()]
            keyboard.send_keys([MODIFIER_KEYS['SHIFT'], keycode])
            if jitter:
                time.sleep(random.randint(0, max_jitter) / 1000.0)
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release keys
            keyboard.send_keys(held_keys) # Keep held keys held
        elif char in SHIFT_REQUIRED_CHARACTERS:
            # Send special characters with Shift
            keycode = SHIFT_REQUIRED_CHARACTERS[char]
            keyboard.send_keys([MODIFIER_KEYS['SHIFT'], keycode])
            if jitter:
                time.sleep(random.randint(0, max_jitter) / 1000.0)
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release keys
            keyboard.send_keys(held_keys) # Keep held keys held
        else:
            print(f"Character '{char}' not found in keycode mapping.")

def replacer(input):
    global constants, variables, random_min, random_max
    # Replace constants and variables in the input
    if "$_RANDOM_INT" in input:
        count = input.count("$_RANDOM_INT")
        for _ in range(count):
            # Replace each $_RANDOM_INT with a random integer between random_min and random_max
            random_value = random.randint(random_min, random_max)
            input = input.replace("$_RANDOM_INT", str(random_value), 1)
    if "$_RANDOM_LOWER_LETTER_KEYCODE" in input:
        # Replace each $_RANDOM_LOWER_LETTER_KEYCODE with a random lowercase letter
        random_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
        input = input.replace("$_RANDOM_LOWER_LETTER_KEYCODE", str(random_letter), 1)
    if "$_RANDOM_UPPER_LETTER_KEYCODE" in input:
        count = input.count("$_RANDOM_UPPER_LETTER_KEYCODE")
        for _ in range(count):
            # Replace each $_RANDOM_UPPER_LETTER_KEYCODE with a random uppercase letter
            random_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            input = input.replace("$_RANDOM_UPPER_LETTER_KEYCODE", str(random_letter), 1)
    if "$_RANDOM_LETTER_KEYCODE" in input:
        count = input.count("$_RANDOM_LETTER_KEYCODE")
        for _ in range(count):
            # Replace each $_RANDOM_LETTER_KEYCODE with a random letter (lowercase or uppercase)
            random_letter = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            input = input.replace("$_RANDOM_LETTER_KEYCODE", str(random_letter), 1)
    if "$_RANDOM_NUMBER_KEYCODE" in input:
        count = input.count("$_RANDOM_NUMBER_KEYCODE")
        for _ in range(count):
            # Replace each $_RANDOM_NUMBER_KEYCODE with a random number
            random_number = random.choice("0123456789")
            input = input.replace("$_RANDOM_NUMBER_KEYCODE", str(random_number), 1)
    if "$_RANDOM_SPECIAL_KEYCODE" in input:
        count = input.count("$_RANDOM_SPECIAL_KEYCODE")
        for _ in range(count):
            # Replace each $_RANDOM_SPECIAL_KEYCODE with a random special character
            special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
            random_char = random.choice(special_chars)
            input = input.replace("$_RANDOM_SPECIAL_KEYCODE", str(random_char), 1)
    if "$_RANDOM_CHAR_KEYCODE" in input:
        count = input.count("$_RANDOM_CHAR_KEYCODE")
        for _ in range(count):
            # Replace each $_RANDOM_CHAR_KEYCODE with a random character (letter, number, or special)
            all_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
            random_char = random.choice(all_chars)
            input = input.replace("$_RANDOM_CHAR_KEYCODE", str(random_char), 1)
    for key in sorted(constants.keys(), key=len, reverse=True):
        input = input.replace(key, str(constants[key]))
    for key in sorted(variables.keys(), key=len, reverse=True):
        input = input.replace(key, str(variables[key]))
    for key in sorted(functions.keys(), key=len, reverse=True):
        if key in input:
            output = ""
            for line in functions[key].split('\n'):
                print(line)
                temp = interpret_line(line.lstrip())
                if temp != None:
                    output += str(temp)
            input = input.replace(key, output)
    return input

def interpret_ducky_script(filename):
    # Wait for the keyboard to be ready
    time.sleep(1)
    # Interpret a DuckyScript file and execute commands
    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        interpret_line(line)

def handle_while_loop(condition, block):
    # Handle While loop execution
    global while_condition, while_block
    while_condition = ""
    while_block = ""
    while eval(replacer(condition)):
        for line in block.split('\n'):
            interpret_line(line.lstrip())

def handle_if_else(conditions, blocks):
    # Handle If-Else block execution
    global if_else_conditions, if_else_blocks, current_if_else
    if_else_conditions = []
    if_else_blocks = []
    current_if_else = 0
    for i, condition in enumerate(conditions):
        if eval(replacer(condition)):
            for line in blocks[i].split('\n'):
                interpret_line(line)
            return

def show_error():
    # Set the red channel to 25% brightness
    np[0] = (64, 0, 0)
    np.write()

def interpret_line(line):
    global rem_block, string_block, stringln_block, mouse_block, constants, variables, num_whiles, num_if_else, reading_while, if_else_conditions, if_else_blocks, current_if_else, reading_if_else, while_condition, while_block, jitter, max_jitter, keypress_delay, reading_function, current_function, functions, random_min, random_max
    # Split the line into parts
    print(line)
    parts = line.strip().split()

    if not parts:
        return # Ignore empty lines
    
    command = parts[0].upper()

    # Ignore REM blocks
    if rem_block:
        if command == 'END_REM':
            rem_block = False
        return

    if command == 'REM_BLOCK':
        rem_block = True
        return

    # Handle STRING and STRINGLN blocks
    if string_block:
        if command == 'END_STRING':
            string_block = False
        else:
            send_string(line.lstrip().rstrip('\n'))
        return
    
    if stringln_block:
        if command == 'END_STRINGLN':
            stringln_block = False
        else:
            send_string(line.lstrip('\t').rstrip('\n') + '\n') # stringln block specifically removes first tab
        return

    # Ignore lines that start with 'REM' as comments
    if command == 'REM':
        return
    
    # While loops, If-Else blocks, and function blocks are handled separately but also need to keep in mind the current state of the other

    # Handle While loop
    if reading_while and not reading_if_else and not reading_function:
        # Append every line to the while_block.
        while_block += line + "\n"  # adding a newline for proper splitting later
        if command == 'WHILE':
            num_whiles += 1
        elif command == 'END_WHILE':
            num_whiles -= 1
            if num_whiles == 0:
                reading_while = False
                handle_while_loop(while_condition, while_block)
        return
    
    if command == 'WHILE' and not reading_if_else and not reading_function:
        reading_while = True
        num_whiles = 1
        while_condition = line.lstrip()[6:].strip()
        while_block = ""  # Start with an empty block
        return
    
    # Handle If-Else blocks
    if command == 'IF' and not reading_while and not reading_function:
        if reading_if_else:
            num_if_else += 1
        else:
            if line.rstrip().endswith('THEN'):
                reading_if_else = True
                if_else_conditions.append(line.strip()[3:-4].strip())
                if_else_blocks.append("")
                return
            else:
                print(f"Invalid IF statement in line '{line.strip()}': Missing 'THEN'")
                show_error()
                return
    
    if command == 'ELSE' and not reading_while and not reading_function:
        if reading_if_else and num_if_else == 0:
            if parts[1] == 'IF':
                if line.rstrip().endswith('THEN'):
                    if_else_conditions.append(line.strip()[8:-4].strip())
                    if_else_blocks.append("")
                    current_if_else += 1
                    return
                else:
                    print(f"Invalid ELSE statement in line '{line.strip()}': Missing 'THEN'")
                    show_error()
                    return
            else:
                if_else_conditions.append("True")
                if_else_blocks.append("")
                current_if_else += 1
                return
        else:
            print(f"Invalid ELSE statement in line '{line.strip()}': Missing 'IF'")
            show_error()
            return
    
    if command == 'END_IF' and not reading_while and not reading_function:
        if reading_if_else:
            if num_if_else > 0:
                num_if_else -= 1
            else:
                reading_if_else = False
                handle_if_else(if_else_conditions, if_else_blocks)
                return
        else:
            print(f"Invalid END_IF statement in line '{line.strip()}': Missing 'IF'")
            show_error()
            return
    
    if reading_if_else and not reading_while and not reading_function:
        if_else_blocks[current_if_else] += line + "\n"
        return
    
    # Handle Functions
    if reading_function and not reading_while and not reading_if_else:
        if command == 'END_FUNCTION':
            reading_function = False
            return
        # Append every line to the function_block.
        functions.update({current_function: functions[current_function] + line + "\n"})  # adding a newline for proper splitting later
        return

    if command == 'FUNCTION' and not reading_while and not reading_if_else:
        reading_function = True
        current_function = line.lstrip()[9:].strip()
        functions.update({current_function: ""})
        return

    if command[-1] == ')' and command[-2] == '(':
        # Call a function
        if command in functions:
            for line in functions[command].split('\n'):
                interpret_line(line.lstrip())
        else:
            print(f"Function '{command}' not found.")
            show_error()
        return
    
    if command == 'RETURN':
        output = ""
        try:
            output = eval(replacer(line.lstrip()[7:]))
        except Exception as e:
            output = replacer(line.lstrip()[7:])
        return output
    
    if command == 'DEFINE':
        # Define a constant
        if len(parts) > 2:
            # Check that the first char is a pound sign
            if parts[1][0] != '#':
                print(f"Invalid constant definition in line '{line.strip()}': Missing '#'")
                show_error()
                return

            # Check if it is String, int, or boolean
            if parts[2].isdigit():
                constants[parts[1]] = int(parts[2])
            elif parts[2].upper() == 'TRUE':
                constants[parts[1]] = True
            elif parts[2].upper() == 'FALSE':
                constants[parts[1]] = False
            else:
                # Check if it needs calculations
                if parts[2][0] == '(':
                    # Get the location of the first parentheses
                    start = line.find('(')

                    expression = replacer(line[start:])
                    
                    # Evaluate the expression
                    try: 
                        constants[parts[1]] = eval(expression) # Evaluate the expression and update the constant
                    except Exception as e:
                        constants[parts[1]] = line.lstrip()[(8 + len(parts[1])):] # Account for the length of the constant name and the 2 spaces
                else:
                    constants[parts[1]] = line.lstrip()[(8 + len(parts[1])):] # Account for the length of the constant name and the 2 spaces
        return
    elif command == 'VAR':
        # Define a variable
        if len(parts) > 3:
            # Check that the first char is a dollar sign
            if parts[1][0] != '$':
                print(f"Invalid variable definition in line '{line.strip()}': Missing '$'")
                show_error()
                return
            # Check if it is String, int, or boolean
            if parts[3].isdigit():
                variables.update({parts[1]: int(parts[3])})
            elif parts[3].upper() == 'TRUE':
                variables.update({parts[1]: True})
            elif parts[3].upper() == 'FALSE':
                variables.update({parts[1]: False})
            else:
                # Check if it needs calculations
                if parts[3][0] == '(':
                    # Get the location of the first parentheses
                    start = line.find('(')

                    expression = replacer(line[start:])
                    
                    # Evaluate the expression
                    try: 
                        variables.update({parts[1]: eval(expression)}) # Evaluate the expression and update the variable
                    except Exception as e:
                        variables.update({parts[1]: line.lstrip()[(7 + len(parts[1])):]}) # Account for the length of the variable name, the 3 spaces and the equal sign
                else:
                    variables.update({parts[1]: line.lstrip()[(7 + len(parts[1])):]}) # Account for the length of the variable name, the 3 spaces and the equal sign
        return
    elif command[0] == '$':
        if command == '$_JITTER_ENABLED':
            if parts[2].upper() == 'TRUE':
                jitter = True
            elif parts[2].upper() == 'FALSE':
                jitter = False
            return
        
        if command == '$_JITTER_MAX':
            max_jitter = int(parts[2])
            return
        
        if command =="$_RANDOM_MIN":
            random_min = int(parts[2])
            return
        
        if command == "$_RANDOM_MAX":
            random_max = int(parts[2])
            return
        
        if len(parts) > 2:

            # Check if it is String, int, or boolean
            if parts[2].isdigit():
                variables.update({parts[0]: int(parts[1])})
            elif parts[2].upper() == 'TRUE':
                variables.update({parts[0]: True})
            elif parts[2].upper() == 'FALSE':
                variables.update({parts[0]: False})
            else:
                # Check if it needs calculations
                if parts[2][0] == '(':
                    # Get the location of the first parentheses
                    start = line.find('(')

                    expression = replacer(line[start:])
                    print(expression)
                    
                    # Evaluate the expression
                    try: 
                        variables.update({parts[0]: eval(expression)}) # Evaluate the expression and update the variable
                    except Exception as e:
                        variables.update({parts[0]: line.lstrip()[(3 + len(parts[0])):]}) # Account for the length of the variable name, the 2 spaces and the equal sign
                else:
                    variables.update({parts[0]: line.lstrip()[(3 + len(parts[0])):]}) # Account for the length of the variable name, the 2 spaces and the equal sign
        return

    newline = replacer(line)
    parts = newline.strip().split()
    if command == 'STRING':
        if len(parts) > 1:
            # Send a string
            send_string(newline.lstrip().rstrip('\n')[7:])
        else:
            string_block = True
    elif command == 'STRINGLN':
        if len(parts) > 1:
            # Send a string followed by a newline
            send_string(newline.lstrip().rstrip('\n')[9:] + '\n')
        else:
            stringln_block = True
    elif command == 'RANDOM_LOWERCASE_LETTER':
        # Send a random lowercase letter
        letter = random.choice("abcdefghijklmnopqrstuvwxyz")
        send_string(letter)
    elif command == 'RANDOM_UPPERCASE_LETTER':
        # Send a random uppercase letter
        letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        send_string(letter)
    elif command == 'RANDOM_LETTER':
        # Send a random letter (lowercase or uppercase)
        letter = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        send_string(letter)
    elif command == 'RANDOM_NUMBER':
        # Send a random number between 0 and 9
        number = random.choice("0123456789")
        send_string(number)
    elif command == 'RANDOM_SPECIAL':
        # Send a random special character
        special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
        char = random.choice(special_chars)
        send_string(char)
    elif command == 'RANDOM_CHAR':
        # Send a random character (letter, number, or special)
        all_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
        char = random.choice(all_chars)
        send_string(char)
    elif command == 'STOP_PAYLOAD':
        print("Stop order received.")
        exit()
    elif command == 'RESTART_PAYLOAD':
        print("Restart order received.")
        interpret_ducky_script("DuckyScript.txt")
        exit()
    elif command == 'HOLD':
        # Hold down a key
        if len(parts) > 1:
            key = parts[1].upper()
            if key in MODIFIER_KEYS and MODIFIER_KEYS[key] not in held_keys:
                held_keys.append(MODIFIER_KEYS[key])
            elif key in SPECIAL_KEYS and SPECIAL_KEYS[key] not in held_keys:
                held_keys.append(SPECIAL_KEYS[key])
            elif key.lower() in CHARACTER_TO_KEYCODE and CHARACTER_TO_KEYCODE[key.lower()] not in held_keys:
                held_keys.append(CHARACTER_TO_KEYCODE[key.lower()])
            else:
                print(f"Key '{key}' not recognized or already held.")
                show_error()
        keyboard.send_keys([])
        keyboard.send_keys(held_keys)
    elif command == 'RELEASE':
        # Release a key
        if len(parts) > 1:
            key = parts[1].upper()
            if key in MODIFIER_KEYS and MODIFIER_KEYS[key] in held_keys:
                held_keys.remove(MODIFIER_KEYS[key])
            elif key in SPECIAL_KEYS and SPECIAL_KEYS[key] in held_keys:
                held_keys.remove(SPECIAL_KEYS[key])
            elif key.lower() in CHARACTER_TO_KEYCODE and CHARACTER_TO_KEYCODE[key.lower()] in held_keys:
                held_keys.remove(CHARACTER_TO_KEYCODE[key.lower()])
            else:
                print(f"Key '{key}' not recognized or not held.")
                show_error()
        keyboard.send_keys([])
        keyboard.send_keys(held_keys)
    elif command == 'MOUSE':
        enable_mouse()
        mouse_block = True
    elif command == 'END_MOUSE':
        disable_mouse()
        mouse_block = False
    elif command == 'MOUSE_MOVE':
        # Move the mouse by a specified amount
        if len(parts) > 2:
            try:
                x = int(parts[1])
                y = int(parts[2])
                if not mouse_block:
                    enable_mouse()
                # mouse can only move max 127 pixels at a time, send multiple commands if needed
                while abs(x) > 127 or abs(y) > 127:
                    mouse.move_by(127 if x > 0 else -127, 127 if y > 0 else -127)
                    x -= 127 if x > 0 else -127
                    y -= 127 if y > 0 else -127
                mouse.move_by(x, y)
            except ValueError:
                print(f"Invalid mouse move parameters in line '{line.strip()}': {parts[1]}, {parts[2]}")
                show_error()
        else:
            print(f"Insufficient parameters for MOUSE_MOVE in line '{line.strip()}'")
            show_error()
        if not mouse_block:
            disable_mouse()
    elif command == 'MOUSE_RIGHT_CLICK':
        try:
            if not mouse_block:
                enable_mouse()
            mouse.click_right(True)
            time.sleep(0.1)  # Short delay to simulate right click
            mouse.click_right(False)
        except Exception as e:
            print(f"Failed to perform right click: {e}")
            show_error()
        if not mouse_block:
            disable_mouse()
    elif command == 'MOUSE_LEFT_CLICK':
        try:
            if not mouse_block:
                enable_mouse()
            mouse.click_left(True)
            time.sleep(0.1)  # Short delay to simulate left click
            mouse.click_left(False)
        except Exception as e:
            print(f"Failed to perform left click: {e}")
            show_error()
        if not mouse_block:
            disable_mouse()
    elif command == 'MOUSE_MIDDLE_CLICK':
        try:
            if not mouse_block:
                enable_mouse()
            mouse.click_middle(True)
            time.sleep(0.1)  # Short delay to simulate middle click
            mouse.click_middle(False)
        except Exception as e:
            print(f"Failed to perform middle click: {e}")
            show_error()
        if not mouse_block:
            disable_mouse()
    elif command in SPECIAL_KEYS:
        # Handle special keys
        keyboard.send_keys([SPECIAL_KEYS[command]])
        if jitter:
                time.sleep(random.randint(0, max_jitter) / 1000.0)
        time.sleep(keypress_delay)
        keyboard.send_keys([])  # Release key
        keyboard.send_keys(held_keys) # Keep held keys held
    elif command == 'DELAY' and len(parts) > 1:
        # Delay for a specified time in milliseconds
        delay_time = int(parts[1]) / 1000.0
        time.sleep(delay_time)
    elif command in MODIFIER_KEYS:
        # Handle multiple modifier keys with a final key (ex. "CTRL ALT DELETE")
        modifiers = []
        keycode = None

        # Collect all modifiers and final key from the command
        for part in parts:
            part_upper = part.upper()
            if part_upper in MODIFIER_KEYS:
                modifiers.append(MODIFIER_KEYS[part_upper])
            elif part_upper in SPECIAL_KEYS:
                keycode = SPECIAL_KEYS[part_upper]
            elif part.lower() in CHARACTER_TO_KEYCODE:
                keycode = CHARACTER_TO_KEYCODE[part.lower()]
            elif part in SHIFT_REQUIRED_CHARACTERS:
                modifiers.append(MODIFIER_KEYS['SHIFT'])
                keycode = SHIFT_REQUIRED_CHARACTERS[part]

        # If we have modifiers and a keycode, send them together
        if modifiers and keycode:
            keyboard.send_keys(modifiers + [keycode])
            if jitter:
                time.sleep(random.randint(0, max_jitter) / 1000.0)
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release keys
            keyboard.send_keys(held_keys) # Keep held keys held
        elif modifiers:
            # If only modifiers were specified, press and release them alone
            keyboard.send_keys(modifiers)
            if jitter:
                time.sleep(random.randint(0, max_jitter) / 1000.0)
            time.sleep(keypress_delay)
            keyboard.send_keys([])  # Release keys
            keyboard.send_keys(held_keys) # Keep held keys held
        else:
            print(f"No key specified for modifiers in command '{line.strip()}'")
            show_error()
    else:
        if command.lower() != 'end_while': # Ignore end_while commands
            print(f"Command '{command}' not recognized or not implemented.")
            show_error()