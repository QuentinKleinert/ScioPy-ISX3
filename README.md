# ISX-3 Frequency Sweep Interface

This Python interface enables communication and control of the ISX-3 Impedance Analyzer from Sciospec via USB 
(virtual COM port). It allows you to configure the device, set up a frequency sweep, start measurements, and save the 
results as a CSV file.


## 📌 Features
- Connect to ISX-3 via serial (USB/COM)

- Configure measurement settings (mode, channel, current/voltage range)

- Define custom frequency sweep (start, stop, points, scale, amplitude)

- Start/stop measurements with repeat cycles

- Save results to a CSV file (measurement_results.csv)


## ⚙️ Requirements
- Python 3.7+
- pyserial

Install dependencies:
``` pip install pyserial ```

## 🧠 Device Overview
- Device: ISX-3 Impedance Analyzer

- Manufacturer: Sciospec Scientific Instruments

- Communication: Serial over USB (virtual COM port)

- Protocol: Byte-level command structure

## 📦 Project Structure
``` src/
└── ISX3.py        # ISX3 communication interface class
main.py            # Example usage and measurement sequence
 ```

## 🚀 Usage Example
```
from src.ISX3 import ISX3

isx3 = ISX3(n_el=4)
isx3.connect_device_FS(port="COM3")  # Set correct COM port

# Set functional settings: mode, channel, current, voltage ranges
isx3.set_fs_settings([0xB0, 0x03, 0x02, 0x01, 0x00, 0xB0])
isx3.get_fs_settings()

# Define frequency sweep: 1 kHz – 10 MHz, 60 points, log scale, 0.1 V amplitude
isx3.set_setup([
    0xB6, 0x16, 0x03,
    0x44, 0x7A, 0x00, 0x00,       # Start Frequency = 1000.0 Hz
    0x4B, 0x18, 0x96, 0x80,       # Stop Frequency = 10,000,000.0 Hz
    0x42, 0xF0, 0x00, 0x00,       # 60 points
    0x01,                         # Logarithmic scale
    0x3F, 0x80, 0x00, 0x00,       # Precision = 1.0
    0x3D, 0xCC, 0xCC, 0xCD,       # Amplitude = 0.1 V
    0xB6                          # End of command
])

# Start measurement (20 cycles)
results = isx3.start_measurement(cycles=20)
print(results)

```

## 📝 Output
Results are saved as:
``` 
measurement_results.csv 
```
With the format: 
``` 
Frequency ID, Real Part, Imaginary Part 
```

## 🧑‍💻 Author
**Quentin Kleinert**

For questions or contributions, feel free to open an issue or pull request.

