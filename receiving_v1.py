#!python3
# -*- coding: UTF-8 -*-

'''
receiving.py   Version 1.0
Automate receiving inventory data entry tasks by selecting (scanning) a scanner mode.
Author: Jesse Weber
Last Updated: 06/25/2019

'''

####################
#     IMPORTS      #
####################

from pynput.keyboard import Key, Controller
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
    print(' ******************************************* ')

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
                sys.exit()
            else:
                port = response.upper()
    return ser

# Iterate through open ports report COM Port that matches scanner description
def checkPorts():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        if '###BARCODE SCANNER DESCRIPTION###' in desc:
            return port
    print('UNABLE TO LOCATE SCANNER. DEFAULTING TO COM3...')
    return 'COM3'
            
# Returns the next scanned data
def NextScan(message, ser):
    
    print(message)
    
    data = '' # Initialize data variable to an empty string
    while len(data) == 0:
        data = ser.read(9999) # get data from barcode scanner
        if len(data) > 0:
            data = str(data) # convert to string
            data = data[2:len(data)-1] # remove prefix and suffix
            
    return data

# Checks for a mode change   
def CheckModeChange(data):

    result = False
    if data[:7] == 'setMode':
        result = True
        
    return result

# Change Mode to &data and return the mode
def ChangeMode(data):
    
    codeKey, value = data.split(':')
    mode = value
    print('\nMODE CHANGED TO: ' + modes[value])
    
    return mode

# Enter &value into Purchase Order Oracle Field then tab X times
def PurchaseOrder(value, X):
    
    keyboard.type(value) # Type Purchase Order
    
    # Press tab X times
    for i in range(X):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        
    print('Entered ' + str(value) + ' into \'Purchase Order\' field')

# Enter &value into Item Number Oracle Field    
def ItemNumber(value):
    
    keyboard.type(value) # Type Item Number and hit enter
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    print('Entered ' + str(value) + ' into \'Item, Rev\' field')
    
# Enter &value into Quantity Orcle Field and check checkbox
def Quantity(value):
    
    keyboard.press(Key.space) # Check checkbox with space
    keyboard.release(Key.space)
    time.sleep(0.1)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    keyboard.type(value) # Enter Quantity
    
    print('Entered ' + str(value) + ' into \'Quantity\' field')

# Enter Subinventory or bypass if not needed
def Subinventory():
    
    # Adjust user view to see Subinventory textbox
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
    data = NextScan('Please scan Subinventory or bypass...', ser)

    if CheckModeChange(data):# Exit if Mode Change
        return data
    
    # If not bypass, enter subinventory name    
    if data == 'bypassSub': 
        print('Bypassing Subinventory...')
    else:
        keyboard.type(data) 
        print('Entered ' + str(data) + ' into \'Subinventory\' field')
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
def setupNext():

    data = NextScan('Please close \'Receipt Header\' window then scan \'Find Receipt Mode\' to continue...', ser)
    if data == 'setMode:findReceipt':
        
        # Close window with F4
        keyboard.press(Key.f4)
        keyboard.release(Key.f4) 
    
        # Open Receipts with Enter
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    return data
    
# Correct Quantity
def correctQuantity(data):

    keyboard.press('-')
    keyboard.release('-')
    keyboard.type(dataQ)
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
        default = 'findReceipt'
        mode = default

        # Continuously listen to COM port
        loop = True
        while loop:

            # Exit - Exit Script
            if mode == 'exit':
                # Double check that they want to exit
                data = NextScan('Scan Exit again to terminate script', ser)
                if data == 'setMode:exit':
                    loop = False
                    continue
                # Check for a mode change
                elif CheckModeChange(data):
                    mode = ChangeMode(data)
                    continue
                else:
                    print('Returning to default mode...')
                    mode = default

            print('\nMODE: ' + modes[mode])
            data = NextScan('Waiting for scan...', ser)   # get data from barcode scanner
        
            # Check for a mode change
            if CheckModeChange(data):
                mode = ChangeMode(data)
                continue
            
            # Type and print data to screen
            if mode == 'printData': 
                keyboard.type(data)
                print(data)

            # bbb - BBB
            elif mode == 'bbb': 
             
                # Purchase Order Field
                PurchaseOrder(data, 7)
                data = NextScan('Please scan Item Number...', ser)
            
                # Check for a mode change
                if CheckModeChange(data):
                    mode = ChangeMode(data)
                    continue
                
                # Purchase Order Field
                ItemNumber(data)
                data = NextScan('Please close \'###\' window then scan Quantity...', ser)
                
                # Check for a mode change
                if CheckModeChange(data):
                    mode = ChangeMode(data)
                    continue
            
                # Quantity Field
                Quantity(data)
            
                # Subinventory Field
                data = Subinventory()
            
                # Check for a mode change
                if CheckModeChange(data):
                    mode = ChangeMode(data)
                    continue
            
                # Close and reopen Receipts Tool
                data = setupNext()
            
                # Check for a mode change
                if CheckModeChange(data):
                    mode = ChangeMode(data)
                    continue
        
            # aaa - AAA
            elif mode == 'aaa':
            
                # Purchase Order Field
                PurchaseOrder(data, 6)
                dataI = NextScan('Please scan Item Number...', ser)
            
                # Check for a mode change
                if CheckModeChange(dataI):
                    mode = ChangeMode(dataI)
                    continue
                
                # Purchase Order Field
                ItemNumber(dataI)
                dataQ = NextScan('Select the appropriate field then scan Quantity...', ser)
            
                # Check for a mode change
                if CheckModeChange(dataQ):
                    mode = ChangeMode(dataQ)
                    continue
            
                correctQuantity(dataQ)
            
                PurchaseOrder(data, 6)
                ItemNumber(dataI)
            
                dataQ = NextScan('Select the appropriate field then scan Quantity...', ser)
            
                # Check for a mode change
                if CheckModeChange(dataQ):
                    mode = ChangeMode(dataQ)
                    continue
                
                correctQuantity(dataQ)
            
        printFooter()

        time.sleep(0.5)
        sys.exit()
    # Remove traceback error on Ctrl^C
    except KeyboardInterrupt:
        sys.exit()
      

if __name__ == "__main__":
    main()
