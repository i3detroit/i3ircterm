import Adafruit_BBIO.GPIO as GPIO
import time
import cp437

#==============================================================================#
#   Beaglebone Black script to interface with Noritake 8-bit Protocol display
#==============================================================================#
#
#   Author: Andrew G. Meyer
#   Date: 2014-11-30

#   Loosely based on lcd.py, an HD44780 driver by Ben Hammel, Erik McKee

#----------------------------------------------------------------------#
#   Pins used to transfer data to the display
#----------------------------------------------------------------------#
PINS = {'E':'P9_24',    # pin 6 on display
        'RS':'P9_23',   # pin 4 on display
        'DB7':'P9_22',  # pin 14 on display
        'DB6':'P9_21',  # pin 13 on display
        'DB5':'P9_20',  # pin 12 on display
        'DB4':'P9_19',  # pin 11 on display
        'DB3':'P9_18',  # pin 10 on display
        'DB2':'P9_17',  # pin 9 on display
        'DB1':'P9_16',  # pin 8 on display
        'DB0':'P9_15'   # pin 7 on display
        }

#----------------------------------------------------------------------#
#   Font Table
#----------------------------------------------------------------------#
#
#   Corresponding 8bit definition for each character
#
CHARS = cp437.transpose()

#----------------------------------------------------------------------#
#   Screen configuration. Default is 24x6 a la CU24063-Y100
#----------------------------------------------------------------------#
ROWS = 6
COLS = 24
         
#----------------------------------------------------------------------#
#   Helper functions 
#----------------------------------------------------------------------#

# Turn all GPIO pins to outputs and set their values to low
def initializePins(pins):
    for pin in pins.itervalues():
        GPIO.setup(pin, GPIO.OUT)
    set_all_low(pins)

# Pause the script for 2 ms
def wait():
    time.sleep(.002)

# Set the GPIO pin to a state that's passed to it 
def set_to_state(pin, state):
    GPIO.output(pin, int(state))

# Turn a pin on 
def set_high(pin):
    set_to_state(pin, GPIO.HIGH)

# Turn a pin off
def set_low(pin):
    set_to_state(pin, GPIO.LOW)

# Turn all pins off
def set_all_low(pins):
    for pin in pins.itervalues():
        set_low(pin)

#----------------------------------------------------------------------#
#   display control 
#----------------------------------------------------------------------#
class Screen:

    # Necessary steps to turn on the display
    def __init__(self, cursor_status='blinking'):

        if bit_mode not in [4,8]:
            bit_mode = 8

        self.bit_mode = bit_mode
        self.pins = dict(PINS)
        
        self.pos_x = 0
        self.pos_y = 0

        # Initialize screen
        initializePins(self.pins)
        self.sendCommand('0x1B')    # command mode
        self.sendCommand('0x40')    # init display
        wait()
        self.on(cursor_status)
        self.scrollMode('vertical')
        self.clear()

    # Tell the display to read in the command 
    def transfer(self):
        set_high(PINS['E'])
        set_all_low(self.pins)

    # Turn the GPIO pins on so the display can read them in 
    def sendCommand(self, command):
        if command.startswith('0x'):
            command = bin(int(command,16))
        set_to_state(PINS['RS'],command[0])
        # Pin R/W is held to ground in the circuit - W only, ignore this bit
        set_to_state(PINS['DB7'], command[2])
        set_to_state(PINS['DB6'], command[3])
        set_to_state(PINS['DB5'], command[4])
        set_to_state(PINS['DB4'], command[5])
        set_to_state(PINS['DB3'], command[6])
        set_to_state(PINS['DB2'], command[7])
        set_to_state(PINS['DB1'], command[8])
        set_to_state(PINS['DB0'], command[9])
        self.transfer()

    # Clear Display
    def clear(self):
        self.sendCommand('0x0C')
        

    # Turn the display on   
    # Turn the cursor on or off and set it's blinking or on or off
    # If nothing is set, or invalid option, set cursor to blinking
    def on(self, cursor_status='blinking'):
        '''
        blinking == underline blinking
        block == block blinking
        underline = underline no blink
        '''
        status_command = {'blinking':'16', 'block':'15', 'underline':'13'}
        try:
            command = '0x' + status_command[cursor_status]
        except:
            command = '0x' + status_command['blinking']
        self.sendCommand(command)

    # Turn the display off
    def off(self):
        self.sendCommand('0x14')

    # Set scroll mode
    def scrollMode(self,mode='vertical'):
        self.sendCommand('0x1F')
        command = {'vertical':0x02,
                   'horizontal':0x03,
                   'overwrite':0x01}[mode]
        self.sendCommand('0x%02x'%command)
    
    # Move cursor
    def moveCursor(self, x, y):
        self.sendCommand('0x1F')        # command mode
        self.sendCommand('0x24')        # move cursor
        self.sendCommand('0x%02x'%x)    # xL is whatever column
        self.sendCommand('0x%02x'%y)    # yL is whatever line
        self.updatePos(x=x,y=y,abs=True)

    # Print a COLS char line to the display
    def printLine(self, line, line_number=1):
        # limit the length of the string, turn the RS pin to high to start
        # data transfer.
        self.moveCursor(line_number)
        if len(line)>COLS:
            line = line[:COLS]

        #  for each character in the line, execute the correct command 
        for char in line:
            self.printChar(char)
            
    def printChar(self,char):
        if char == '\x08': #backspace
            self.sendCommand('0x08')
            self.updatePos(x=-1)
        try:
            command = CHARS[char]
        except:
            command = CHARS['?']
        self.sendCommand(command)
        self.updatePos(x=1)
        
    def updatePos(self,x=0,y=0,abs=False):
        if abs:
            if not (0 <= x < COLS):
                x = COLS - 1
            if not (0 <= y < ROWS):
                y = ROWS - 1
            self.pos_x = x
            self.pos_y = y
        else:
            if self.pos_x + x >= COLS:
                self.x = 0
                y += 1
            elif self.pos_x + x < 0:
                self.pos_x = COLS - 1
                y -= 1
            else:
                self.pos_x += x
            if not (0 <= self.pos_y + y < ROWS):
                self.pos_y = 0
            elif self.pos_y + y < 0:
                self.pos_y = ROWS - 1
            else:
                self.pos_y += y
