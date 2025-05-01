# Steps to install Keithley interactive code on Windows

## Install Python 3.12.9

Went to python.org and installed the 64 bit program in my App directory 
```bash
C:\Users\sng_a\AppData\Local\Programs\Python\Python312\
```

## Install Python Extension in VSCode

Standard ms (microsoft store?) package.  Unistalled the debugger

## Added Python to the System PATH

**Add Python to PATH manually**
   Here's how:
   1. Press Windows key + X and select "System"
   2. Click on "Advanced system settings" on the right
   3. Click "Environment Variables" button
   4. Under "System Variables", find and select "Path"
   5. Click "Edit"
   6. Click "New"
   7. Add these two paths (replace with your actual Python installation path):
      ```
      C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312\
      C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312\Scripts\
      ```
   8. Click "OK" on all windows to save

## Change the PowerShell execution policy to allow running the virtual environment activation script

1. **Run PowerShell as Administrator**
   - Right-click on PowerShell in the Start menu
   - Select "Run as Administrator"

2. **Set the Execution Policy**
   Run this command:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   - Type 'Y' when prompted to confirm

3. **Return to VSCode**
   - Close your current terminal in VSCode
   - Open a new terminal
   - The virtual environment should now activate automatically

This is a one-time setup for PowerShell on your Windows machine. After doing this, your virtual environment should activate without any security errors.

## Activate Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

## Install pyvisa packages

```powershell
pip install pyvisa
pip install pyvisa-py
```

## Download NI-VISA

Decided to install the most recent version 
[NI-VISA 2025 Q1](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html)


## To use the Keithley may need to do slow startup from PowerShell

if you encounter the issue [Hardware Not Detected in NI MAX after Upgrading Windows](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9ErSAK&l=en-US&OpenDocument&prodref=com-ni-package_manager-25.0) you will want to force a full startup

```powershell
shutdown /r /t 0
```

## Download the Drivers for the GPIB to USB connector

We are using the [KUSB-488B](https://www.mouser.com/datasheet/2/403/KUSB-488B-903-01_Sept2018_KUSB-488B-903-01B-1868459.pdf) GPIB to USB connector.  

To use this we need to download the drivers from the Tektronix site.  I am using this download of the [Version 5.0.0](https://www.tek.com/en/accessory/ki-488/5-0-0) which is also good for windows 10 and 11 as well.  

I am chosing the installation option for NI Command Compatible

The download automatically installs te software in the following directory
```
C:\Program Files (x86)\Keithley Instruments\KI-488\
```

## Requirements for the existing code

gpib-ctypes==0.3.0
ifaddr==0.2.0
PyVISA==1.14.1
PyVISA-py==0.7.2
typing_extensions==4.13.0
zeroconf==0.146.5

## MUST turn of FAST Startup in WIndows 11!!


Yes, the Shift key method is a more thorough way to ensure a complete shutdown. Let me update the instructions:

# Windows Setup for Keithley Instruments

## Required: Disable Fast Startup
Fast Startup must be disabled for proper GPIB device detection. Follow these steps:

1. Open **Control Panel**
2. Go to **Power Options**
3. Click **Choose what the power buttons do**
4. Click **Change settings that are currently unavailable**
5. Uncheck ✓ **Turn on fast startup (recommended)**
6. Click **Save changes**

## Proper Shutdown Procedure
After disabling Fast Startup, perform a full shutdown:

1. Save all work
2. Hold down **Shift** key
3. Click Start Menu → Power → **Shut Down**
4. Keep holding Shift until screen goes black
5. Wait 30 seconds after shutdown
6. Power on your computer
7. Wait for full boot-up
8. Connect to Keithley instruments

> **Important**: The Shift key method forces Windows to perform a complete shutdown instead of a hybrid shutdown, ensuring all devices are properly reinitialized on next boot.

---
*Note: These settings may need to be checked again after Windows updates.*
