import pyvisa as visa
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

# rm = visa.ResourceManager()
# P = rm.list_resources()
# ds_gpib_address = 2


# result = list(map(lambda x: x.find(str(ds_gpib_address)), P))
# dev_num = np.argmax(result)
# keithley = rm.open_resource(P[dev_num])
# print(keithley.query('*IDN?'))

try:
    rm = visa.ResourceManager()
    keithley = rm.open_resource('GPIB0::2::INSTR')
    keithley.timeout = 20000  # Add timeout like GUI version
    print(keithley.query('*IDN?'))
except Exception as e:
    print("Connection error:", str(e))
    exit()

#2400/2400-LV/2401 — Current limit can be set from 1nA to 1.05A, and the voltage
#limit can be set from 200μV to 210V (21V for 2400-LV and 2401).
# Voltage compliance for Keithley 2400 is muliple of *10 increment .
#current compliance for Keithley 2400 is muliple of *5 increment.
# V_compliance must be (+/-)10mv,.1v,1v or 10v more than V_range(depending on how big the range is)
#and I_compliance must be (+/-).05uA,.5uA,5uA,.05mA,5mA,.05A,.5A,5A more than I_range(depending on how
#big the range is)
V_compliance = 21 #200
V_range = 2      #200

I_compliance =  10e-3  #100e-6
I_range =  10e-3       #1e-1

# Choose either Voltage sweep or Current sweep mode.
voltsourcemode = 1
currsourcemode = 0

# Backsweep
backsweep = 0

########################################################################################################################
# Start and stop parameters can be both V and I.
# Put decimal places e.g. start = -3.0 / stop = 3.0
start =  -1
stop = 1
num_steps = 10
delay = 0.1        # Reduced from 0.5 to 0.1 seconds
delay_auto = 0.3
NPLC = 1.0        # Reduced from 3.0 to 1.0 for faster measurements

ct = time.localtime()
gate_voltage = -0
project_name = 'CDI590'
device_name = 'FixTest_1'
file_name = project_name + '_' + device_name + time.strftime("_%Y%m%d_") + \
            str(ct.tm_hour) + str(ct.tm_min) + str(ct.tm_sec)
########################################################################################################################

out_V = []
out_I = []
output = []
###########
data_file=[]
temp_step=10

# Voltage Sweep
if voltsourcemode:
    # Clear and reset instrument first
    keithley.write('*CLS')  # Clear status
    keithley.write('*RST')  # Reset instrument
    time.sleep(0.1)  # Small delay after reset
    
    # Setup commands with delays between each
    commands = [
        ':sour:func volt',
        ':sour:volt:mode fix',
        f':sour:volt:range {V_range}',
        ':sens:func "curr"',
        'sense:current:range:auto on',
        f':sens:curr:prot {I_compliance}',
        f':sens:curr:nplc {NPLC}',
        f':sour:del {delay}',
        ':display:digits maximum'
    ]
    
    for cmd in commands:
        keithley.write(cmd)
        time.sleep(0.05)  # Reduced from 0.1 to 0.05 seconds
    
    # Turn on output after setup
    keithley.write(':outp on')
    time.sleep(0.2)  # Reduced from 0.5 to 0.2 seconds
    
    # Start from 0V and gradually move to start voltage
    V = 0.0
    steps_to_start = 5 # Reduced from 10 to 5 steps
    for v in np.linspace(0, start, steps_to_start):
        keithley.write(f':sour:volt:lev {v}')
        time.sleep(delay)
        keithley.query('*OPC?')  # Wait for operation complete
    
    # Main sweep
    for v in np.linspace(start, stop, num_steps + 1):
        keithley.write(f':sour:volt:lev {v}')
        time.sleep(delay)  # Ensure settling time
        keithley.query('*OPC?')  # Wait for operation complete
        
        # Take measurement with retry
        max_retries = 3
        for retry in range(max_retries):
            try:
                keithley.write(':read?')
                data = keithley.read()
                break
            except visa.VisaIOError:
                if retry == max_retries - 1:
                    raise
                time.sleep(0.5)
        
        out_V.append(float(data.split(',')[0]))
        out_I.append(float(data.split(',')[1]))
        output.append([float(data.split(',')[0]), float(data.split(',')[1])])
    
    # Gradually return to 0V
    for v in np.linspace(stop, 0, steps_to_start):
        keithley.write(f':sour:volt:lev {v}')
        time.sleep(delay)
    
    # Turn off output
    keithley.write(':outp off')
    keithley.close()

# Current Sweep
if currsourcemode:
    keithley.write('*rst')
    keithley.write(':syst:beep:stat 1')
    keithley.write(':sour:func curr')
    keithley.write(':sour:curr:mode fix')
    keithley.write(':sour:curr:range ' + str(I_range))
    keithley.write('sense:voltage:range ' + str(V_range))
    if delay_auto:
        keithley.write(':sour:del:auto on')
    if not delay_auto:
        keithley.write(':sour:del ' + str(delay))
    keithley.write(':sens:func "volt"')
    keithley.write(':sens:volt:prot ' + str(V_compliance))# set compliance limit
    keithley.write(':sens:volt:nplc ' + str(NPLC))
    keithley.write(':outp on')# turn on the output mode

    # loop for current sweep.

    #++++++++++ START +++++++++
    # sweeping from 0 to start (lower limit)
    I = 0.0
    
    for loopI in range(temp_step):
            keithley.write(':sour:curr:lev ' + str(I))
            keithley.write(':read?')#Trigger sweep, request data.
            temp_data = keithley.read()

            I = I + (float(start)/temp_step)
            
    #++++++++++++ END ++++++++++++

    # sweeping from lower limit to upper limit
    
    if not backsweep:
        for loopI in range(num_steps + 1):
            keithley.write(':sour:curr:lev ' + str(I))
            keithley.write(':read?')#Trigger sweep, request data.
            data = keithley.read()
            out_I.append(float(data[0:13]))
            out_V.append(float(data[14:27]))
            output.append([float(data[0:13]), float(data[14:27])])

            I = I + (float(stop) - float(start))/num_steps

        #++++++++++ START +++++++++
        # sweeping from stop(upper limit) to 0.

        for loopI in range(temp_step):
            keithley.write(':sour:curr:lev ' + str(I))
            keithley.write(':read?')#Trigger sweep, request data.
            temp_data = keithley.read()
            if I <= 0:
                break
            else:
                I = I - (float(stop)/num_steps)
        
    

        #++++++++++++ END ++++++++++++
        #Turn off output mode.
        keithley.write(':outp off')

    if backsweep:
        for loopI in range(num_steps):# loopI is a variable that executes form 0 to num_steps
            keithley.write(':sour:curr:lev ' + str(I))
            keithley.write(':read?')#Trigger sweep, request data.
            data = keithley.read()  # save the output in 

            out_I.append(float(data[0:13]))
            out_V.append(float(data[14:27]))
            output.append([float(data[0:13]), float(data[14:27])])
            data_file.append(float(data))

            if I >= stop:
                break
            else:
                I = I + (stop - start)/num_steps

        for loopI in range(num_steps + 1):
            keithley.write(':sour:curr:lev ' + str(I))
            keithley.write(':read?')
            data = keithley.read()

            out_I.append(float(data[0:13]))
            out_V.append(float(data[14:27]))
            output.append([float(data[0:13]), float(data[14:27])])

            I = I - (stop - start)/num_steps

        keithley.write(':outp off')

# write in csv file
with open(file_name + '.csv', 'w', newline='') as myfile:# 'w' will create or overwrite an existing file.
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)# csv.QUOTE_ALL will put quotation marks on all the values
    header = [['Volt(V)', 'Current(A)']]
    wr.writerows(header)
    wr.writerows(output)# write all the data of output into the file
print(file_name)

# save npz file
out_V = np.array(out_V)
out_I = np.array(out_I)
np.savez(file_name, V=out_V, I=out_I)

# Plot the IV curve
plt.xlabel('Voltage(Volts)')
plt.ylabel('Current(Amps)')
plt.plot(out_V, out_I, '-o')
plt.show()
