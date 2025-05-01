import tkinter as tk
from tkinter import ttk
import pyvisa as visa
import time
import matplotlib.pyplot as plt
import csv
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class KeithleyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keithley 2401 IV Measurement")
        
        # Create main frames
        self.setup_frame = ttk.LabelFrame(root, text="Measurement Setup", padding="10")
        self.setup_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Source Mode Selection
        ttk.Label(self.setup_frame, text="Source Mode:").grid(row=0, column=0, pady=5)
        self.source_mode = ttk.Combobox(self.setup_frame, 
                                      values=["Voltage Source", "Current Source"],
                                      state="readonly")
        self.source_mode.set("Voltage Source")
        self.source_mode.grid(row=0, column=1, pady=5)
        
        # Voltage Range
        ttk.Label(self.setup_frame, text="Voltage Range (V):").grid(row=1, column=0, pady=5)
        self.voltage_range = ttk.Combobox(self.setup_frame, 
                                        values=["2", "20"],
                                        state="readonly")
        self.voltage_range.set("2")
        self.voltage_range.grid(row=1, column=1, pady=5)
        
        # Current Compliance
        ttk.Label(self.setup_frame, text="Current Compliance:").grid(row=2, column=0, pady=5)
        self.current_compliance = ttk.Combobox(self.setup_frame, 
                                             values=["1µA", "10µA", "100µA", "1mA", "10mA", "100mA", "1A"],
                                             state="readonly")
        self.current_compliance.set("10mA")
        self.current_compliance.grid(row=2, column=1, pady=5)
        
        # Sweep Parameters
        sweep_frame = ttk.LabelFrame(self.setup_frame, text="Sweep Parameters", padding="10")
        sweep_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")
        
        ttk.Label(sweep_frame, text="Start (V):").grid(row=0, column=0, pady=5)
        self.start_voltage = ttk.Entry(sweep_frame)
        self.start_voltage.insert(0, "-1")
        self.start_voltage.grid(row=0, column=1, pady=5)
        
        ttk.Label(sweep_frame, text="Stop (V):").grid(row=1, column=0, pady=5)
        self.stop_voltage = ttk.Entry(sweep_frame)
        self.stop_voltage.insert(0, "1")
        self.stop_voltage.grid(row=1, column=1, pady=5)
        
        ttk.Label(sweep_frame, text="Steps:").grid(row=2, column=0, pady=5)
        self.steps = ttk.Entry(sweep_frame)
        self.steps.insert(0, "100")
        self.steps.grid(row=2, column=1, pady=5)
        
        ttk.Label(sweep_frame, text="Delay (s):").grid(row=3, column=0, pady=5)
        self.delay = ttk.Entry(sweep_frame)
        self.delay.insert(0, "0.1")
        self.delay.grid(row=3, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=4, column=0, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Measurement", 
                                     command=self.start_measurement)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                    command=self.stop_measurement)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=5)
        
        self.is_measuring = False

    def compliance_to_float(self, compliance_str):
        """Convert compliance string to float value"""
        multipliers = {'µA': 1e-6, 'mA': 1e-3, 'A': 1}
        for unit, mult in multipliers.items():
            if unit in compliance_str:
                return float(compliance_str.replace(unit, '')) * mult
        return float(compliance_str)

    def start_measurement(self):
        try:
            # Get parameters from GUI
            v_range = float(self.voltage_range.get())
            i_compliance = self.compliance_to_float(self.current_compliance.get())
            start = float(self.start_voltage.get())
            stop = float(self.stop_voltage.get())
            steps = int(self.steps.get())
            delay = float(self.delay.get())
            
            # Initialize Keithley with longer timeout
            rm = visa.ResourceManager()
            keithley = rm.open_resource('GPIB0::2::INSTR')
            keithley.timeout = 20000  # Set timeout to 20 seconds
            
            # Basic instrument setup and verification
            keithley.write('*CLS')  # Clear status
            keithley.write('*RST')  # Reset instrument
            
            # Verify communication
            idn = keithley.query('*IDN?')
            print(f"Connected to: {idn}")
            
            # Setup measurement with error checking
            commands = [
                ':sour:func volt',
                ':sour:volt:mode fix',
                f':sour:volt:range {v_range}',
                ':sens:func "curr"',
                f':sens:curr:prot {i_compliance}',
                f':sour:del {delay}',
                ':outp on'
            ]
            
            for cmd in commands:
                keithley.write(cmd)
                time.sleep(0.1)  # Small delay between commands
            
            # Clear plot
            self.ax.clear()
            out_V = []
            out_I = []
            
            # Perform sweep with error checking
            self.is_measuring = True
            for v in np.linspace(start, stop, steps):
                if not self.is_measuring:
                    break
                    
                try:
                    # Set voltage with verification
                    keithley.write(f':sour:volt:lev {v}')
                    time.sleep(delay)  # Ensure settling time
                    
                    # Take measurement with retry
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            keithley.write(':read?')
                            data = keithley.read()
                            break
                        except visa.VisaIOError as e:
                            if retry == max_retries - 1:
                                raise
                            time.sleep(0.5)
                    
                    voltage = float(data.split(',')[0])
                    current = float(data.split(',')[1])
                    
                    out_V.append(voltage)
                    out_I.append(current)
                    
                    # Update plot
                    self.ax.clear()
                    self.ax.plot(out_V, out_I, '-o')
                    self.ax.set_xlabel('Voltage (V)')
                    self.ax.set_ylabel('Current (A)')
                    self.canvas.draw()
                    
                    # Update GUI
                    self.root.update()
                    
                except Exception as e:
                    print(f"Error at voltage {v}: {str(e)}")
                    continue
            
            # Safely turn off output
            try:
                keithley.write(':outp off')
                keithley.close()
            except:
                pass
            
            # Save data if measurements were successful
            if out_V and out_I:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"IV_measurement_{timestamp}"
                np.savez(filename, V=out_V, I=out_I)
                
                with open(filename + '.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Voltage(V)', 'Current(A)'])
                    writer.writerows(zip(out_V, out_I))
                
        except Exception as e:
            error_msg = f"Measurement Error: {str(e)}\n\nPlease check:\n"
            error_msg += "1. Is the Keithley turned on?\n"
            error_msg += "2. Is the GPIB cable properly connected?\n"
            error_msg += "3. Is the GPIB address correct (set to 2)?\n"
            error_msg += "4. Are the voltage/current ranges appropriate?"
            tk.messagebox.showerror("Error", error_msg)
            
            # Try to safely close connection
            try:
                keithley.write(':outp off')
                keithley.close()
            except:
                pass

    def stop_measurement(self):
        self.is_measuring = False

if __name__ == "__main__":
    root = tk.Tk()
    app = KeithleyGUI(root)
    root.mainloop()
