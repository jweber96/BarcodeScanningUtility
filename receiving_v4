#!python3
# -*- coding: UTF-8 -*-

'''
receiving.py   Version 1.4
    This scanner utility utilizes pyserial and pynput to automate an inventory 
    data entry process via barcode scanning. The utility iterates over open 
    COM Ports to match to a specific scanner description, then assigns that 
    port using pyserial. Pynput uses keyboard shortcuts to navigate a database 
    and enters barcode data. Several QR code 'modes' can be scanned at any 
    point of a data entry process to back out/change modes.
Author: Jesse Weber
Last Updated: 08/12/2019

'''

####################
#     IMPORTS      #
####################

from pynput.keyboard import Key, Controller
import datetime
import getpass
import os
import os.path
import re
import serial
import serial.tools.list_ports
import sys
import time

# Initialize Modes
modes = {
    'exit':'\'Exit Script\'',
    '### aaa ###':'\'### AAA ###\'',
    '### bbb ###':'\'### BBB ###\'',
    'printData':'\'Print Data\''
    }
# Initialize QR Code Struct
class QRCode(object):
    def __init__(self, PO, IN, L, Q):
        self.PurchaseOrder = PO
        self.ItemNumber = IN
        self.Line = L
        self.Quantity = Q
     
        
####################
#    FUNCTIONS     #
####################

# Separates QR Code string of data and returns struct
def separateQR(string):
    PO,IN,L,Q = string.split("#")
    return QRCode(PO,IN,L,Q)

# Print string then flush ouput to the log file incase of improper exit
def printLog(text):

    # Get Current Time
    ts = time.time()
    ds = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S : ')
    if text == '\n':
        print(ds)
    else:
        print(ds + text)
    
    # Flush the output
    sys.stdout.flush()

# Open Log File and replace it if size > Specified Size
def openLogFile(user):

    maxSize = 100       ### <-- ENTER SIZE LIMIT IN MB HERE ###

    maxSize = maxSize * pow(10, 6) # Convert to bytes

    fname = 'C:\\Users\\' + user + '\\AppData\\Scanner\\ReceivingLog.txt'
    old = re.sub('.txt', 'Old.txt', fname)       

    if fileSize(fname) < maxSize:
        return open(fname, 'a+') # Append log file
    else:
        # Archive old log and open new log
        if os.path.exists(old):
            os.remove(old) # Delete existing old log
        if os.path.exists(fname):
            os.rename(fname, old) # Rename current log to old
        return open(fname, 'w+') # Write to new log
    
# Get File Size of &fname
def fileSize(fname):

    size = 0
    if os.path.exists(fname):
        size = os.stat(fname).st_size
    return size

# Print Header including &user
def printHeader(user):
    
    # Get Current Time
    ts = time.time()
    ds = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    printLog('******************************************* ')
    printLog('*    RECEIVING BARCODE SCANNER UTILITY    * ')
    printLog('*    Written/Developed by: Jesse Weber    * ')
    printLog('*          Current User: ' + user + '          * ')
    printLog('*           ' + ds + '           * ')
    printLog('******************************************* ')

# Print Footer
def printFooter():

    printLog('\n')
    printLog('******************************************* ')
    printLog('*              Exiting script             * ')
    printLog('******************************************* \n\n')

# Presses tab (positive number) and shift tab (negative number) &num times
def pressTab(keyboard, num):
    if num > 0:
        for _ in range(num): 
            keyboard.press(Key.tab)
            keyboard.release(Key.tab) 
    else:
        for _ in range(abs(num)):
            with keyboard.pressed(Key.shift):
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)

# Presses Shift + Page_Down
def shiftPgDn(keyboard):
    keyboard.press(Key.shift)
    keyboard.press(Key.shift_r)
    keyboard.press(Key.page_down)
    keyboard.release(Key.page_down)
    keyboard.release(Key.shift_r)
    keyboard.release(Key.shift)

# Change Windows using Alt + W then window number &num
def changeWindows(keyboard, num):
    with keyboard.pressed(Key.alt):
        keyboard.press('w')
        keyboard.release('w')

    keyboard.press(str(num))
    keyboard.release(str(num))

# Assign Scanner COM Port to serial
def setupCOMPort():

    port = checkPorts()
    try:
        ser = serial.Serial(port, 115200, timeout=0)
    except OSError:
        printLog('SCANNER NOT FOUND ON PORT: ' + str(port))
        sys.exit()
    return ser

# Iterate through open ports report COM Port that matches scanner description
def checkPorts():

    ports = serial.tools.list_ports.comports()
    # Iterate over ports
    for port, desc, hwid in sorted(ports):
        # If description matches, report that port
        if '##### BARCODE SCANNER DESCRIPTION TO MATCH #####' in desc:
            return port
    printLog('UNABLE TO LOCATE SCANNER. DEFAULTING TO COM3...')
    return 'COM3'
            
# Returns the next scanned data
def nextScan(text, ser):
    
    printLog(text)
    data = '' # Initialize data variable to an empty string
    while len(data) == 0:
        data = ser.read(9999) # get data from barcode scanner
        if len(data) > 0:
            data = str(data) # convert to string
            data = data[2:len(data)-1] # remove prefix and suffix
    return data

# Checks for a mode change, returns a boolean
def checkModeChange(data):

    result = False
    if len(data) > 7 and data[:7] == 'setMode':
        result = True
    return result

# Change Mode to &data and return the mode without the prefix
def changeMode(data):
    
    if len(data) > 7:
        # Trim prefix
        mode = data[8:]
        printLog('\n')
        printLog('MODE CHANGED TO: ' + modes[mode])
        printLog('\n')
    else:
        mode = data
    
    return mode

# Set default mode and return it
def setDefaultMode(ser):

    selection = False
    
    while not selection:
        data = nextScan('Scan a mode to begin...', ser)
        
        # Check for a mode change
        if checkModeChange(data):
            default = changeMode(data)
            selection = True
            
            # Avoid exit as default mode
            if default == 'exit':
                default = 'findReceipt'
                
    return default

# Enter &POvalue into Purchase Order Oracle Field then tab X times
def purchaseOrder(keyboard, POvalue, numTabs):
    
    keyboard.type(POvalue) # Type Purchase Order
    
    # Press tab numTabs times
    pressTab(keyboard, numTabs)
        
    printLog('Entered ' + str(POvalue) + ' into \'Purchase Order\' field')

# Enter &INvalue into Item Number Oracle Field and hit enter
def itemNumber(keyboard, INvalue):
    
    # Type Item Number and hit enter
    keyboard.type(INvalue)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    printLog('Entered ' + str(INvalue) + ' into \'Item, Rev\' field')
    
# Switch windows, enter &Qvalue into Quantity Oracle Field and check checkbox
def quantity(keyboard, Qvalue):

    # Change to Receipts block with Shift + Page Down
    shiftPgDn(keyboard)

    # Check checkbox with space
    keyboard.press(Key.space)
    keyboard.release(Key.space)

    # Tab over and enter Quantity
    pressTab(keyboard, 1)
    keyboard.type(Qvalue)
    
    printLog('Entered ' + str(Qvalue) + ' into \'Quantity\' field')

# Enter subinventory or bypass if not needed
def subinventory(keyboard, ser):
    
    # Adjust user view to see subinventory textbox
    pressTab(keyboard, 10)
    pressTab(keyboard, -2)
    
    # Wait for scan to see what to do
    data = nextScan('Waiting for subinventory or bypass...', ser)

    # Check for mode change
    if not checkModeChange(data):
        # Check for bypass or subinventory
        if data == 'bypassSub': 
            printLog('Bypassing subinventory...')
        else:
            keyboard.type(data) 
            printLog('Entered ' + str(data) + ' into \'subinventory\' field')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        
        # Save changes
        with keyboard.pressed(Key.ctrl): 
            keyboard.press('s')
            keyboard.release('s')
            
        # Switch to Receipt Window
        changeWindows(keyboard, 4)
    
    # Return data in case of Mode Change
    return data
    
# Set up next receipt
def setupNext(keyboard, ser):

    data = nextScan('Waiting for \'Find Receipt Mode\' scan to continue...', ser)
    if checkModeChange(data) and changeMode(data) == 'findReceipt':
        
        # Switch windows to be able to close
        changeWindows(keyboard, 2)

        # Close window with F4
        keyboard.press(Key.f4)
        keyboard.release(Key.f4) 
    
        # Open Receipts with Enter
        keyboard.type('r')
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    return data
    
# Correct Quantity
def correctQuantity(keyboard, Qvalue, ser):

    # Select which field to correct 
    data = nextScan('Waiting for confirmation...', ser)

    # Check for a mode change
    if checkModeChange(data):
        return data
    elif data == 'bypassSub':
        printLog('Bypassed \'Quantity\' field')
    else:
        keyboard.press('-')
        keyboard.release('-')
        keyboard.type(Qvalue)
        printLog('Entered -' + str(Qvalue) + ' into \'Correction\' field')
    

    
    with keyboard.pressed(Key.ctrl): 
        keyboard.press('s')
        keyboard.release('s')
    
    # Close window with F4
    keyboard.press(Key.f4)
    keyboard.release(Key.f4) 
    
    # Open Corrections with Enter
    keyboard.type('c')
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    pressTab(keyboard, 3)
    return data
    
# BBB
def bbbProcedure(keyboard, ser):

    # Scan QR Code
    data = nextScan('Waiting for Receipt QR scan...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        return changeMode(data)
    
    # Separate string into class QR
    QR = separateQR(data)
    
    # Purchase Order Field
    purchaseOrder(keyboard, QR.PurchaseOrder, 7)
    
    # Item Number Field
    itemNumber(keyboard, QR.ItemNumber)

    # Quantity Field
    quantity(keyboard, QR.Quantity)

    # Subinventory Field
    data = subinventory(keyboard, ser)

    # Check for a mode change
    if checkModeChange(data):
        return changeMode(data)

    # Close and reopen Receipts Tool
    data = setupNext(keyboard, ser)

    # Check for a mode change
    if not data == 'setMode:aaa' and checkModeChange(data):
        return changeMode(data)
    
    return data

# AAA Procedure
def aaaProcedure(keyboard, ser):

    # Scan QR Code
    data = nextScan('Waiting for Correction QR scan...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        return changeMode(data)
    
    # Separate string into class QR
    QR = separateQR(data)

    # Enter Purchase Order, Item Number and Corrected Quantity
    for _ in range(2): 
        purchaseOrder(keyboard, QR.PurchaseOrder, 6)
        itemNumber(keyboard, QR.ItemNumber)
        data = correctQuantity(keyboard, QR.Quantity, ser)
        # Check for a mode change
        if checkModeChange(data):
            return changeMode(data)

    return data

# Print Data Procedure
def printDataProcedure(keyboard, ser):
    
    data = nextScan('Waiting for scan...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        return changeMode(data)
    else:
        keyboard.type(data)
        printLog(data)
        return 'printData'

# Exit Procedure - Returns True if Exit Mode is scanned again
def exitProcedure(ser):
    
    # Double check that they want to exit
    data = nextScan('Scan Exit again to terminate script', ser)
    return data, not changeMode(data) == 'exit'
    


####################
#       MAIN       #
####################

def main():
    
    try:
        # Get Current User
        user = getpass.getuser()

    except ImportError:
        printLog('ImportError: Unable to identify user')
        sys.exit()

    try:    
        # Open Log File
        sys.stdout = openLogFile(user)
        
    except IOError:
        printLog('IOError: Unable to open file')
        sys.exit()
    
    try:
        # Header
        printHeader(user)

        # Set up COM port and controller
        ser = setupCOMPort()
        keyboard = Controller()

        # Set default mode
        default = setDefaultMode(ser)
        mode = default

        # Initialize data to empty
        data = ''
        
        # Loop until exit is scanned twice
        loop = True
        while loop:
            
            try:
                printLog('MODE: ' + modes[mode])
            except:
                printLog('Returning to default mode...')
                mode = default
                continue

            # Exit - Exit Script Procedure 
            if mode == 'exit':
                mode, loop = exitProcedure(ser)
                continue
                    
            # Print Data - Type and print data to screen
            elif mode == 'printData': 
                mode = printDataProcedure(keyboard, ser)
                continue

            # BBB
            elif mode == 'bbb': 
                mode = bbbProcedure(keyboard, ser)
                continue
                
            # AAA
            elif mode == 'aaa':
                mode = aaaProcedure(keyboard, ser)
                continue
            
            # Check for a mode change
            if checkModeChange(data):
                mode = changeMode(data)
                continue
        
    # Remove traceback error on Ctrl^C
    except KeyboardInterrupt:
        printLog('KeyboardInterrupt')
    finally:
        printFooter()
        time.sleep(0.2)
        sys.exit()

if __name__ == "__main__":
    main()
