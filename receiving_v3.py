#!python3
# -*- coding: UTF-8 -*-

'''
receiving.py   Version 1.1
Automate receiving inventory data entry tasks by selecting (scanning) a scanner mode.
Author: Jesse Weber
Last Updated: 07/11/2019

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
    'printData':'\'Print Data\'',
    'findReceipt':'\'Find Expected Receipts\'',
    'exit':'\'Exit Script\'',
    'findCorrection':'\'Find Correction\''
    }

####################
#    FUNCTIONS     #
####################

# Print string then flush ouput to the log file incase of improper exit
def printLog(text):

    # Get Current Time
    ts = time.time()
    ds = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S : ')
    if text == '\n':
        print(ds)
    else:
        print(ds + text)
    sys.stdout.flush()

# Open Log File and replace it if size > 200MB?
def openLogFile(user):

    fname = 'C:\\Users\\' + user + '\\AppData\\Scanner\\ReceivingLog.txt'
    old = re.sub('.txt', 'Old.txt', fname)
    
    maxSize = 200       ### <-- ENTER SIZE LIMIT IN MB HERE ###            
    
    maxSize = maxSize * pow(10, 6) # Convert to bytes
    if fileSize(fname) < maxSize:
        return open(fname, 'a+') # Append log file
    else:
        # Archive old log and open new log
        if os.path.exists(old):
            os.remove(old) # Delete existing old log
        if os.path.exists(fname):
            os.rename(fname, old) # Rename current log to old
        return open(fname, 'w+') # Write to new log
    
# Get File Size    
def fileSize(fname):

    size = 0
    if os.path.exists(fname):
        size = os.stat(fname).st_size
    return size

# Print Header
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

# Assign Scanner COM Port to serial
def setupCOMPort():

    port = checkPorts()
    scannerCheck = False
    while not scannerCheck:
        try:
            ser = serial.Serial(port, 115200, timeout=0)
            scannerCheck = True
        except OSError as e:
            printLog('SCANNER NOT FOUND ON PORT: ' + str(port))
            printLog('Enter COM port name or \'Exit\' to quit')
            response = input()
            if response.lower() == 'exit':
                sys.exit()
            else:
                port = response.upper()
    return ser

# Iterate through open ports report COM Port that matches scanner description
def checkPorts():

    ports = serial.tools.list_ports.comports()
    # Iterate over ports
    for port, desc, hwid in sorted(ports):
        # If description matches, report that port
        if '### SCANNER DESCRIPTION ###' in desc:
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
    if data[:7] == 'setMode':
        result = True
    return result

# Change Mode to &data and return the mode
def changeMode(data):
    
    # Trim prefix
    prefix, mode = data.split(':')
    
    printLog('\n')
    printLog('MODE CHANGED TO: ' + modes[mode])
    printLog('\n')
    
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
            
            # Don't allow exit as default mode
            if default == 'exit':
                default = 'findReceipt'
                
    return default

# Enter &value into Purchase Order Oracle Field then tab X times
def purchaseOrder(keyboard, value, numTabs):
    
    keyboard.type(value) # Type Purchase Order
    
    # Press tab numTabs times
    for i in range(numTabs):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        
    printLog('Entered ' + str(value) + ' into \'Purchase Order\' field')

# Enter &value into Item Number Oracle Field    
def itemNumber(keyboard, value):
    
    # Type Item Number and hit enter
    keyboard.type(value)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    printLog('Entered ' + str(value) + ' into \'Item, Rev\' field')
    
# Enter &value into Quantity Oracle Field and check checkbox
def quantity(keyboard, value):
    
    # Check checkbox with space
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    time.sleep(0.1)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    keyboard.type(value) # Enter Quantity
    
    printLog('Entered ' + str(value) + ' into \'Quantity\' field')

# Enter subinventory or bypass if not needed
def subinventory(keyboard, ser):
    
    # Adjust user view to see subinventory textbox
    for i in range(10): 
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
    for i in range(2):
        with keyboard.pressed(Key.shift):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        time.sleep(0.1)
        
    # Wait for scan to see what to do
    data = nextScan('Please scan subinventory or bypass...', ser)

    if checkModeChange(data):# Exit if Mode Change
        return data
    
    # If not bypass, enter subinventory name    
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
    with keyboard.pressed(Key.alt):
        keyboard.press('w')
        keyboard.release('w')

    keyboard.press('4')
    keyboard.release('4')
    
    # Return data in case of Mode Change
    return data
    
# Set up next receipt
def setupNext(keyboard, ser):

    data = nextScan('Please close \'Receipt Header\' window then scan \'Find Receipt Mode\' to continue...', ser)
    if data == 'setMode:findReceipt':
        
        # Close window with F4
        keyboard.press(Key.f4)
        keyboard.release(Key.f4) 
    
        # Open Receipts with Enter
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    return data
    
# Correct Quantity
def correctQuantity(keyboard, data):

    keyboard.press('-')
    keyboard.release('-')
    keyboard.type(data)
    
    printLog('Entered -' + str(data) + ' into \'Quantity\' field')
    
    with keyboard.pressed(Key.ctrl): 
        keyboard.press('s')
        keyboard.release('s')
    
    # Close window with F4
    keyboard.press(Key.f4)
    keyboard.release(Key.f4) 
    
    # Open Corrections with Enter
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    for i in range(3): 
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
    
# Find Receipt Procedure
def findReceiptProcedure(keyboard, ser):

    # Purchase Order Field
    data = nextScan('Waiting for Purchase Order...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode
    
    purchaseOrder(keyboard, data, 7)
    data = nextScan('Waiting for Item Number...', ser)

    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode
    
    # Purchase Order Field
    itemNumber(keyboard, data)
    data = nextScan('Please close \'Receipt Header\' window then scan Quantity...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode

    # Quantity Field
    quantity(keyboard, data)

    # Subinventory Field
    data = subinventory(keyboard, ser)

    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode

    # Close and reopen Receipts Tool
    data = setupNext(keyboard, ser)

    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode
    return 'findReceipt'

# Find Correction Procedure
def findCorrectionProcedure(keyboard, ser):

    # Purchase Order Field
    dataP = nextScan('Waiting for Purchase Order...', ser)
    
    # Check for a mode change
    if checkModeChange(dataP):
        mode = changeMode(dataP)
        return mode
        
    purchaseOrder(keyboard, dataP, 6)
    dataI = nextScan('Waiting for Item Number...', ser)

    # Check for a mode change
    if checkModeChange(dataI):
        mode = changeMode(dataI)
        return mode
    
    # Purchase Order Field
    itemNumber(keyboard, dataI)
    dataQ = nextScan('Select the appropriate field then scan Quantity...', ser)

    # Check for a mode change
    if checkModeChange(dataQ):
        mode = changeMode(dataQ)
        return mode

    correctQuantity(keyboard, dataQ)

    purchaseOrder(keyboard, dataP, 6)
    itemNumber(keyboard, dataI)

    dataQ = nextScan('Select the appropriate field then scan Quantity...', ser)

    # Check for a mode change
    if checkModeChange(dataQ):
        mode = changeMode(dataQ)
        return mode
    
    correctQuantity(keyboard, dataQ)
    return 'findCorrection'

# Print Data Procedure
def printDataProcedure(keyboard, ser):
    
    data = nextScan('Waiting for scan...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode
    else:
        keyboard.type(data)
        printLog(data)
        return 'printData'

# Exit Procedure
def exitProcedure(ser):
    
    # Double check that they want to exit
    data = nextScan('Scan Exit again to terminate script', ser)
    if data == 'setMode:exit':
        return False
    return True


####################
#       MAIN       #
####################

def main():
    
    try:
        # Get Current User
        user = getpass.getuser()
        
        # Open Log File
        sys.stdout = openLogFile(user)
        
    except IOError:
        printLog('IOError: Unable to open file')
        printFooter()
        time.sleep(0.2)
        sys.exit()
    
    try:
        # Header
        printHeader(user)

        # Set up COM port and controller
        ser = setupCOMPort()
        keyboard = Controller()
        time.sleep(0.2)

        # Set default mode
        default = setDefaultMode(ser)
        mode = default
        data = ''
        
        # Continuously listen to COM port
        loop = True
        while loop:

            printLog('MODE: ' + modes[mode])
            sys.stdout.flush()
                
            # Exit - Exit Script Procedure
            if mode == 'exit':
                if exitProcedure(ser):
                    printLog('Returning to default mode...')
                    mode = default
                    data = ''
                else:
                    loop = False
                    
            # Type and print data to screen
            elif mode == 'printData': 
                mode = printDataProcedure(keyboard, ser)
                continue

            # Receiving - Find Expected Receipt Procedure
            elif mode == 'findReceipt': 
                mode = findReceiptProcedure(keyboard, ser)
                continue
                
            # Correction - Find Correction Procedure
            elif mode == 'findCorrection':
                mode = findCorrectionProcedure(keyboard, ser)
                continue
            
            # Check for a mode change
            if checkModeChange(data):
                mode = changeMode(data)
                data = ''
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
