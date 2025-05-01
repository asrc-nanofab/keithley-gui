import pyvisa as visa
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

# Try different VISA backends
try:
    # First try the NI-VISA backend
    rm = visa.ResourceManager()
    print("Using NI-VISA backend")
except:
    # If that fails, try the py-VISA backend
    rm = visa.ResourceManager('@py')
    print("Using py-VISA backend")

# Print all available resources
print("Available resources:", rm.list_resources())

# Instead of automatic detection, directly specify the instrument address
# Try one of these formats depending on your connection:

try:
    # For GPIB connection (if address is 2):
    keithley = rm.open_resource('GPIB0::2::INSTR')
    
    # If that doesn't work, try these alternatives:
    # keithley = rm.open_resource('GPIB::2::0::INSTR')
    # keithley = rm.open_resource('GPIB::2::INSTR')
    
    print("Successfully connected to:", keithley.query('*IDN?'))
except Exception as e:
    print("Connection error:", str(e))
    print("\nPlease verify:")
    print("1. GPIB address matches the instrument (check front panel)")
    print("2. NI-VISA or another VISA implementation is properly installed")
    print("3. The instrument is powered on and properly connected")
    exit()

# Rest of your code continues here...