# Keithley IV Measurement GUI User Manual

## Initial Setup
### Model Selection
- Choose between `Keithley 2400` (GPIB 1) or `Keithley 2401` (GPIB 2)
  - `2400`: Voltage range up to 200V
  - `2401`: Voltage range up to 20V

## Measurement Settings Guide

### 1. Source Mode
- **Voltage Source**: For standard IV measurements (most common)
  - You control voltage, measure current
- **Current Source**: For specialized measurements
  - You control current, measure voltage

### 2. Range Settings
> **Important**: Ranges and compliance values are interdependent!

#### For Voltage Source Mode:
1. **Voltage Range**
   ```
   2401: 0.2V, 2V, 20V
   2400: 0.2V, 2V, 20V, 200V
   ```
   - Choose the smallest range that covers your sweep range
   - Must be ≥ your maximum sweep voltage

2. **Current Range**
   ```
   Options: 1µA, 10µA, 100µA, 1mA, 10mA, 100mA, 1A
   ```
   - Must be ≥ your current compliance
   - Choose based on expected current

3. **Compliance Settings**
   - `Current Compliance` must be ≤ `Current Range`
   - `Voltage Compliance` should be ≥ `Voltage Range`

#### For Current Source Mode:
1. **Current Range**
   - Must be ≥ your maximum sweep current
   - Choose the smallest range that covers your sweep range

2. **Voltage Range**
   - Must be ≥ your voltage compliance
   - `2401`: Max 20V
   - `2400`: Max 200V

### 3. Sweep Parameters
1. **Start and Stop Values**
   - Must be within your selected voltage/current range
   - Example: For 2V range, keep within ±2V

2. **Number of Steps**
   ```
   Recommended: 100-1000 points
   More points = smoother curve but longer measurement
   ```

3. **Delay**
   ```
   Minimum: 0.1s recommended
   Increase for high-impedance measurements
   ```
   - Too short: noisy data
   - Too long: very slow measurement

4. **NPLC** (Number of Power Line Cycles)
   ```
   0.01: Fastest, noisiest
   1.0:  Good balance (recommended)
   10.0: Slowest, lowest noise
   ```

## Best Practices

### For Most IV Measurements:
```
Start with:
- Voltage Source Mode
- 2V Voltage Range
- 10mA Current Range
- 10mA Current Compliance
- 1.0 NPLC
- 0.1s Delay
- 100 steps
```

### Then adjust based on your device:
- High resistance: 
  ```
  ↑ Increase voltage range
  ↓ Decrease current compliance
  ```
- Low resistance:
  ```
  ↓ Decrease voltage range
  ↑ Increase current compliance
  ```

### Common Mistakes to Avoid:
1. Setting compliance higher than range
2. Setting sweep values outside the selected range
3. Using too short delay times
4. Setting current compliance too high for sensitive devices

### Safety Tips:
- [ ] Always start with conservative compliance values
- [ ] Verify settings before connecting device
- [ ] Monitor the first few measurements for compliance issues

## Troubleshooting

### Compliance Errors:
```
Check:
✓ Is sweep range within voltage range?
✓ Is current compliance appropriate?
✓ Are ranges properly set for compliance values?
```

### Noisy Data:
```
Try:
✓ Increase NPLC
✓ Increase delay time
✓ Use smaller ranges if possible
✓ Check shielding/grounding
```

### No Measurements:
```
Verify:
✓ GPIB addresses match instruments
✓ All connections are secure
✓ Output is enabled
✓ Compliance settings aren't too restrictive
```

---
*Note: This manual assumes basic familiarity with electrical measurements and Keithley instruments.*
