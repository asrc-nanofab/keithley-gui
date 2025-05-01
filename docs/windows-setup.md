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
