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
isx3.connect_device_FS(port="COM3") # change to com port if necessary

isx3.set_fs_settings(
    measurement_mode= 2,
    measurement_channel="Main Port",
    current_measurement_range="10mA",
    voltage_measurement_range="autoranging"
    )

isx3.set_setup(
    start_frequency="1kHz",
    end_frequency="10MHz",
    count=10,
    scale="log",
    precision=1.0,
    amplitude="100mV",
    excitation_type="voltage"
)


results = isx3.start_measurement(spectres=15)

print(results)

```

## 📝 Output
```
Successfully Connected to COM3. 

Command-Acknowledge: Command has been executed successfully
message buffer:
 ['0x18', '0x1', '0x83', '0x18']
message length:	 4
Response from device:  b'\x18\x01\x82\x18'
FS settings applied.

Set the setup. 

Starts the measuring for 2 Cycles...
4 Measuring Results were written into measurement_results.csv.
Command-Acknowledge: Command has been executed successfully
message buffer:
 ['0x18', '0x1', '0x83', '0x18']
message length:	 4
[(0, 96.88323974609375, 0.014319001697003841), (1, 96.76373291015625, 3.699613571166992), (0, 96.87141418457031, -0.003805396379902959), (1, 96.75221252441406, 3.7035341262817383)]

Process finished with exit code 0
```

## 🧑‍💻 Author
**Quentin Kleinert**

For questions or contributions, feel free to open an issue or pull request.
Or contact me: quentinkleinert850@gmail.com

