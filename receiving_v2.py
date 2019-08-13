#!python3
# -*- coding: UTF-8 -*-

'''
receiving.py   Version 1.1
Automate receiving inventory data entry tasks by selecting (scanning) a scanner mode.
Author: Jesse Weber
Last Updated: 06/27/2019

'''

####################
#     IMPORTS      #
####################

from pynput.keyboard import Key, Controller
import os
import re
import serial
import serial.tools.list_ports
import sys
import time

# Initialize Modes
modes = {
    'printData':'\'Print Data\'',
    'bbb':'\'BBB\'',
    'exit':'\'Exit Script\'',
    'aaa':'\'AAA\''
    }

####################
#    FUNCTIONS     #
####################

# Print Header
def printHeader():
    print('\n ******************************************* ')
    print(' *    RECEIVING BARCODE SCANNER UTILITY    * ')
    print(' ******************************************* ')
    print(' *    Written/Developed by Jesse Weber     * ')
    print(' ******************************************* \n')

# Print Footer
def printFooter():
    print('\n ******************************************* ')
    print(' *              Exiting script             * ')
    print(' ******************************************* ')

# Assign Scanner COM Port to serial
def setupCOMPort():
    port = checkPorts()
    scannerCheck = False
    while not scannerCheck:
        try:
            ser = serial.Serial(port, 115200, timeout=0)
            scannerCheck = True
        except OSError as e:
            print('SCANNER NOT FOUND ON PORT: ' + str(port))
            print('Enter COM port name or \'Exit\' to quit')
            response = input()
            if response.lower() == 'exit':
                printFooter()
                time.sleep(0.5)
                sys.exit()
            else:
                port = response.upper()
    return ser

# Iterate through open ports report COM Port that matches scanner description
def checkPorts():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        if '###SCANNER DESCRIPTION###' in desc:
            return port
    print('UNABLE TO LOCATE SCANNER. DEFAULTING TO COM3...')
    return 'COM3'
            
# Returns the next scanned data
def nextScan(message, ser):
    
    print(message)
    
    data = '' # Initialize data variable to an empty string
    while len(data) == 0:
        data = ser.read(9999) # get data from barcode scanner
        if len(data) > 0:
            data = str(data) # convert to string
            data = data[2:len(data)-1] # remove prefix and suffix
            
    return data

# Checks for a mode change   
def checkModeChange(data):

    result = False
    if data[:7] == 'setMode':
        result = True
    return result

# Change Mode to &data and return the mode
def changeMode(data):
    
    prefix, value = data.split(':')
    mode = value
    print('\nMODE CHANGED TO: ' + modes[value])
    return mode

# Set default mode and return it
def setDefaultMode(ser):
    selection = False
    while not selection:
        data = nextScan('Scan a mode to begin...', ser)
        if checkModeChange(data):
            default = changeMode(data)
            selection = True
            # Correct exit as default mode
            if default == 'exit':
                default = 'printData'
    return default

# Enter &value into Purchase Order Oracle Field then tab X times
def purchaseOrder(keyboard, value, numTabs):
    
    keyboard.type(value) # Type Purchase Order
    
    # Press tab numTabs times
    for i in range(numTabs):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        
    print('Entered ' + str(value) + ' into \'Purchase Order\' field')

# Enter &value into Item Number Oracle Field    
def itemNumber(keyboard, value):
    
    keyboard.type(value) # Type Item Number and hit enter
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    print('Entered ' + str(value) + ' into \'Item, Rev\' field')
    
# Enter &value into Quantity Oracle Field and check checkbox
def quantity(keyboard, value):
    
    keyboard.press(Key.space) # Check checkbox with space
    keyboard.release(Key.space)
    time.sleep(0.1)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    keyboard.type(value) # Enter Quantity
    
    print('Entered ' + str(value) + ' into \'Quantity\' field')

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
        print('Bypassing subinventory...')
    else:
        keyboard.type(data) 
        print('Entered ' + str(data) + ' into \'subinventory\' field')
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

    data = nextScan('Please close \'###\' window then scan \'BBB\' to continue...', ser)
    if data == 'setMode:bbb':
        
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
    
# BBB Procedure
def bbbProcedure(keyboard, ser):

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
    data = nextScan('Please close \'###\' window then scan Quantity...', ser)
    
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
    return 'bbb'

# AAA Procedure
def aaaProcedure(keyboard, ser):

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
    return 'aaa'

# Print Data Procedure
def printDataProcedure(keyboard, ser):
    
    data = nextScan('Waiting for scan...', ser)
    
    # Check for a mode change
    if checkModeChange(data):
        mode = changeMode(data)
        return mode
    else:
        keyboard.type(data)
        print(data)
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
        # Header
        printHeader()

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

            print('\nMODE: ' + modes[mode])
                
            # Exit - Exit Script
            if mode == 'exit':
                # loop = exitProcedure(ser)
                if exitProcedure(ser):
                    print('Returning to default mode...')
                    mode = default
                    data = ''
                else:
                    loop = False
                    
            # Type and print data to screen
            elif mode == 'printData': 
                mode = printDataProcedure(keyboard, ser)
                continue

            # bbb - BBB
            elif mode == 'findReceipt': 
                mode = bbbProcedure(keyboard, ser)
                continue
                
            # aaa - AAA
            elif mode == 'aaa':
                mode = aaaProcedure(keyboard, ser)
                continue
            
            # Check for a mode change
            if checkModeChange(data):
                mode = changeMode(data)
                data = ''
                continue
        
        printFooter()
        time.sleep(0.5)
        sys.exit()
    # Remove traceback error on Ctrl^C
    except KeyboardInterrupt:
        sys.exit()
      

if __name__ == "__main__":
    main()
