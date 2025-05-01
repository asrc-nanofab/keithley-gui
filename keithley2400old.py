import pyvisa as visa
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

rm = visa.ResourceManager()
P = rm.list_resources()
ds_gpib_address = 2

result = list(map(lambda x: x.find(str(ds_gpib_address)), P))
dev_num = np.argmax(result)
keithley = rm.open_resource(P[dev_num])
print(keithley.query('*IDN?'))

# Voltage compliance for Keithley 2400 is 240010 V
V_compliance = 250
V_range = 250

I_compliance = .00001
I_range = .1

# Choose either Volt sweep or Current sweep mode.
voltsourcemode = 1
currsourcemode = 0

# Backsweep
backsweep = 0

########################################################################################################################
# Start and stop parameters can be both V and I.
# Put decimal places e.g. start = -3.0 / stop = 3.0
start = -1
stop = 2
num_steps = 100
delay =.2
delay_auto = 0
NPLC = 1.0      # 0.01 to 10.00

ct = time.localtime()
gate_voltage = 0.0
project_name = 'GEC_'
device_name = 'w-10_l-5'
file_name = project_name + 'Vg_' + str(gate_voltage) + 'V_' + device_name + time.strftime("_%Y%m%d_") + \
            str(ct.tm_hour) + str(ct.tm_min) + str(ct.tm_sec)
########################################################################################################################

out_V = []
out_I = []
output = []

# Voltage Sweep
if voltsourcemode:
    keithley.write('*rst')
    keithley.write(':syst:beep:stat 1')
    keithley.write(':sour:func volt')
    keithley.write(':sour:volt:mode fix')
    keithley.write(':sour:volt:range ' + str(V_range))
    keithley.write('sense:current:range ' + str(I_range))
    if delay_auto:
        keithley.write(':sour:del:auto on')
    if not delay_auto:
        keithley.write(':sour:del ' + str(delay))
    keithley.write(':sens:func "curr"')
    keithley.write(':sens:curr:prot ' + str(I_compliance))
    keithley.write(':sens:curr:nplc ' + str(NPLC))
    keithley.write(':outp on')

    V = start

    if not backsweep:
        for loopV in range(num_steps + 1):
            keithley.write(':sour:volt:lev ' + str(V))
            keithley.write(':read?')
            data = keithley.read()
            out_V.append(float(data[0:13]))
            out_I.append(float(data[14:27]))
            output.append([float(data[0:13]), float(data[14:27])])

            V = V + (float(stop) - float(start))/num_steps

        keithley.write(':outp off')

    if backsweep:
        for loopV in range(num_steps):
            keithley.write(':sour:volt:lev ' + str(V))
            keithley.write(':read?')
            data = keithley.read()

            out_V.append(float(data[0:13]))
            out_I.append(float(data[14:27]))
            output.append([float(data[0:13]), float(data[14:27])])

            if V >= stop:
                break
            else:
                V = V + (stop - start)/num_steps

        for loopV in range(num_steps + 1):
            keithley.write(':sour:volt:lev ' + str(V))
            keithley.write(':read?')
            data = keithley.read()

            out_V.append(float(data[0:13]))
            out_I.append(float(data[14:27]))
            output.append([float(data[0:13]), float(data[14:27])])
            V = V - (stop - start)/num_steps

        keithley.write(':outp off')

# write in csv file
with open(file_name + '.csv', 'w', newline='') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    header = [['Volt(V)', 'Current(A)']]
    wr.writerows(header)
    wr.writerows(output)
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

# TODO: INCOMPLETE ###
# Current Sweep