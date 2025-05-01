import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyvisa as visa
import time
import matplotlib.pyplot as plt
import csv
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class KeithleyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keithley 2400/2401 IV Measurement")
        
        # Define model-specific parameters with GPIB addresses
        self.model_configs = {
            'Keithley 2400': {
                'gpib_address': 'GPIB0::1::INSTR',
                'voltage_ranges': ["0.2", "2", "20", "200"],
                'current_ranges': ["1µA", "10µA", "100µA", "1mA", "10mA", "100mA", "1A"],
                'max_voltage': 200,
                'max_current': 1.05
            },
            'Keithley 2401': {
                'gpib_address': 'GPIB0::2::INSTR',
                'voltage_ranges': ["0.2", "2", "20"],
                'current_ranges': ["1µA", "10µA", "100µA", "1mA", "10mA", "100mA", "1A"],
                'max_voltage': 20,
                'max_current': 1.05
            }
        }
        
        # Create main frames
        self.setup_frame = ttk.LabelFrame(root, text="Measurement Setup", padding="10")
        self.setup_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Model Selection with GPIB info
        ttk.Label(self.setup_frame, text="Model:").grid(row=0, column=0, pady=5)
        self.model_var = tk.StringVar()
        self.model_select = ttk.Combobox(self.setup_frame, 
                                       values=list(self.model_configs.keys()),
                                       textvariable=self.model_var,
                                       state="readonly")
        self.model_select.set("Keithley 2401")  # Default to 2401
        self.model_select.grid(row=0, column=1, pady=5)
        self.model_select.bind('<<ComboboxSelected>>', self.update_ranges)
        
        # Display GPIB address
        self.gpib_label = ttk.Label(self.setup_frame, text="GPIB: 2")  # Default to 2401
        self.gpib_label.grid(row=0, column=2, pady=5, padx=5)
        
        # Source Mode Selection
        ttk.Label(self.setup_frame, text="Source Mode:").grid(row=1, column=0, pady=5)
        self.source_mode = ttk.Combobox(self.setup_frame, 
                                      values=["Voltage Source", "Current Source"],
                                      state="readonly")
        self.source_mode.set("Voltage Source")
        self.source_mode.grid(row=1, column=1, pady=5)
        self.source_mode.bind('<<ComboboxSelected>>', self.update_ranges)
        
        # Voltage Range
        ttk.Label(self.setup_frame, text="Voltage Range (V):").grid(row=2, column=0, pady=5)
        self.voltage_range = ttk.Combobox(self.setup_frame, state="readonly")
        self.voltage_range.grid(row=2, column=1, pady=5)
        
        # Current Range
        ttk.Label(self.setup_frame, text="Current Range:").grid(row=3, column=0, pady=5)
        self.current_range = ttk.Combobox(self.setup_frame, state="readonly")
        self.current_range.grid(row=3, column=1, pady=5)
        
        # Compliance Frame
        compliance_frame = ttk.LabelFrame(self.setup_frame, text="Compliance Settings", padding="10")
        compliance_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
        
        ttk.Label(compliance_frame, text="Voltage Compliance (V):").grid(row=0, column=0, pady=5)
        self.voltage_compliance = ttk.Combobox(compliance_frame, state="readonly")
        self.voltage_compliance.grid(row=0, column=1, pady=5)
        
        ttk.Label(compliance_frame, text="Current Compliance:").grid(row=1, column=0, pady=5)
        self.current_compliance = ttk.Combobox(compliance_frame, state="readonly")
        self.current_compliance.grid(row=1, column=1, pady=5)
        
        # Sweep Parameters
        sweep_frame = ttk.LabelFrame(self.setup_frame, text="Sweep Parameters", padding="10")
        sweep_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")
        
        ttk.Label(sweep_frame, text="Start:").grid(row=0, column=0, pady=5)
        self.start_value = ttk.Entry(sweep_frame)
        self.start_value.insert(0, "-1")
        self.start_value.grid(row=0, column=1, pady=5)
        
        ttk.Label(sweep_frame, text="Stop:").grid(row=1, column=0, pady=5)
        self.stop_value = ttk.Entry(sweep_frame)
        self.stop_value.insert(0, "1")
        self.stop_value.grid(row=1, column=1, pady=5)
        
        ttk.Label(sweep_frame, text="Steps:").grid(row=2, column=0, pady=5)
        self.steps = ttk.Entry(sweep_frame)
        self.steps.insert(0, "100")
        self.steps.grid(row=2, column=1, pady=5)
        
        ttk.Label(sweep_frame, text="Delay (s):").grid(row=3, column=0, pady=5)
        self.delay = ttk.Entry(sweep_frame)
        self.delay.insert(0, "0.1")
        self.delay.grid(row=3, column=1, pady=5)
        
        # NPLC Setting
        ttk.Label(sweep_frame, text="NPLC:").grid(row=4, column=0, pady=5)
        self.nplc = ttk.Combobox(sweep_frame, 
                                values=["0.01", "0.1", "1.0", "3.0", "10.0"],
                                state="readonly")
        self.nplc.set("1.0")
        self.nplc.grid(row=4, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=6, column=0, pady=10)
        
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
        
        # Initialize ranges
        self.update_ranges(None)

        # Add Data Storage Frame
        data_frame = ttk.LabelFrame(self.setup_frame, text="Data Storage", padding="10")
        data_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="nsew")

        # Project/Experiment Name
        ttk.Label(data_frame, text="Project Name:").grid(row=0, column=0, pady=5)
        self.project_name = ttk.Entry(data_frame)
        self.project_name.insert(0, "experiment")
        self.project_name.grid(row=0, column=1, columnspan=2, pady=5, sticky="ew")

        # Sample/Device Name
        ttk.Label(data_frame, text="Sample Name:").grid(row=1, column=0, pady=5)
        self.sample_name = ttk.Entry(data_frame)
        self.sample_name.insert(0, "sample1")
        self.sample_name.grid(row=1, column=1, columnspan=2, pady=5, sticky="ew")

        # Save Path Preview
        ttk.Label(data_frame, text="Save Path:").grid(row=2, column=0, pady=5)
        self.save_path_var = tk.StringVar()
        self.save_path_label = ttk.Label(data_frame, textvariable=self.save_path_var, wraplength=300)
        self.save_path_label.grid(row=2, column=1, columnspan=2, pady=5)

        # Bind updates to path preview
        self.project_name.bind('<KeyRelease>', self.update_save_path)
        self.sample_name.bind('<KeyRelease>', self.update_save_path)

        # Initialize save path
        self.update_save_path(None)

    def update_ranges(self, event):
        model = self.model_var.get()
        config = self.model_configs[model]
        
        # Update GPIB display
        gpib_addr = config['gpib_address'].split('::')[1]
        self.gpib_label.config(text=f"GPIB: {gpib_addr}")
        
        # Update voltage range options
        self.voltage_range['values'] = config['voltage_ranges']
        if not self.voltage_range.get() in config['voltage_ranges']:
            self.voltage_range.set(config['voltage_ranges'][1])  # Set to 2V by default
            
        # Update current range options
        self.current_range['values'] = config['current_ranges']
        if not self.current_range.get() in config['current_ranges']:
            self.current_range.set(config['current_ranges'][4])  # Set to 10mA by default
            
        # Update compliance options based on source mode
        if self.source_mode.get() == "Voltage Source":
            self.voltage_compliance['values'] = config['voltage_ranges']
            self.current_compliance['values'] = config['current_ranges']
            if not self.voltage_compliance.get() in config['voltage_ranges']:
                self.voltage_compliance.set(config['voltage_ranges'][-1])
            if not self.current_compliance.get() in config['current_ranges']:
                self.current_compliance.set(config['current_ranges'][4])
        else:
            self.current_compliance['values'] = config['current_ranges']
            self.voltage_compliance['values'] = config['voltage_ranges']
            if not self.current_compliance.get() in config['current_ranges']:
                self.current_compliance.set(config['current_ranges'][-1])
            if not self.voltage_compliance.get() in config['voltage_ranges']:
                self.voltage_compliance.set(config['voltage_ranges'][1])

    def compliance_to_float(self, compliance_str):
        """Convert compliance string to float value"""
        multipliers = {'µA': 1e-6, 'mA': 1e-3, 'A': 1}
        for unit, mult in multipliers.items():
            if unit in compliance_str:
                return float(compliance_str.replace(unit, '')) * mult
        return float(compliance_str)

    def update_save_path(self, event):
        """Update the save path preview based on current inputs"""
        project = self.project_name.get().strip()
        sample = self.sample_name.get().strip()
        
        # Create example path
        timestamp = time.strftime("%Y%m%d")
        base_path = os.path.join('DATA', project, f"{timestamp}_{sample}")
        self.save_path_var.set(base_path)

    def get_save_path(self):
        """Generate the actual save path with creation of directories"""
        project = self.project_name.get().strip()
        sample = self.sample_name.get().strip()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Create base path
        base_path = os.path.join('DATA', project)
        
        # Create directories if they don't exist
        if not os.path.exists('DATA'):
            os.makedirs('DATA')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            
        # Full path for this measurement
        return os.path.join(base_path, f"{timestamp}_{sample}")

    def start_measurement(self):
        try:
            # Get save path first
            save_path = self.get_save_path()
            
            # Get current model configuration
            model = self.model_var.get()
            config = self.model_configs[model]
            gpib_address = config['gpib_address']
            
            # Initialize Keithley with model-specific address
            rm = visa.ResourceManager()
            keithley = rm.open_resource(gpib_address)
            keithley.timeout = 20000
            
            # Verify correct instrument
            idn = keithley.query('*IDN?')
            print(f"Connected to: {idn}")
            
            if model == 'Keithley 2400' and '2400' not in idn:
                raise Exception(f"Expected Keithley 2400 at GPIB 1, found: {idn}")
            elif model == 'Keithley 2401' and '2401' not in idn:
                raise Exception(f"Expected Keithley 2401 at GPIB 2, found: {idn}")
            
            # Get measurement parameters
            v_range = float(self.voltage_range.get())
            i_compliance = self.compliance_to_float(self.current_compliance.get())
            start = float(self.start_value.get())
            stop = float(self.stop_value.get())
            steps = int(self.steps.get())
            delay = float(self.delay.get())
            
            # Verify ranges are within model limits
            if abs(v_range) > config['max_voltage']:
                raise Exception(f"Voltage range exceeds {model} limit of {config['max_voltage']}V")
            
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
            
            # Use save_path for files
            if out_V and out_I:
                # Save NPZ file
                np.savez(save_path, V=out_V, I=out_I)
                
                # Save CSV file
                with open(save_path + '.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Voltage(V)', 'Current(A)'])
                    writer.writerows(zip(out_V, out_I))
                
                # Save plot
                plt.figure()
                plt.plot(out_V, out_I, '-o')
                plt.xlabel('Voltage (V)')
                plt.ylabel('Current (A)')
                plt.title(f'IV Curve - {self.model_var.get()} - {self.sample_name.get()}')
                plt.savefig(save_path + '.png')
                plt.close()
                
                # Update plot in GUI
                self.ax.clear()
                self.ax.plot(out_V, out_I, '-o')
                self.ax.set_xlabel('Voltage (V)')
                self.ax.set_ylabel('Current (A)')
                self.canvas.draw()
                
                # Show save confirmation with actual path
                messagebox.showinfo("Success", 
                                  f"Data saved in:\n{os.path.dirname(save_path)}\n\n"
                                  f"Files saved as:\n{os.path.basename(save_path)}.*")

        except Exception as e:
            error_msg = f"Measurement Error: {str(e)}\n\nPlease check:\n"
            error_msg += f"1. Is the {model} connected to GPIB {gpib_address}?\n"
            error_msg += "2. Is the instrument turned on?\n"
            error_msg += "3. Are the measurement parameters within range?"
            messagebox.showerror("Error", error_msg)
            
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