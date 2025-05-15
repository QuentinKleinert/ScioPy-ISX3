import struct
import serial
import serial.tools.list_ports
import csv
import check_User_Input as input_user
from itertools import chain
import util


class ISX3:
    def __init__(self, n_el: int) -> None:
        self.n_el = n_el
        self.serial_protocol = None
        self.device = None
        self.frequency_points = 0


    def is_port_available(self, port: str) -> bool:
        """Check if the specified COM port is available."""
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        return port in available_ports

    def connect_device_FS(self, port: str):
        """Connect to ISX-3 via virtual COM port (USB)."""
        self.serial_protocol = "FS"

        if not self.is_port_available(port):
            print(f"Error: Port {port} is not available.")
            return

        try:
            self.device = serial.Serial(
                port=port,
                baudrate=9600,
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
            )
            print(f"Connected to {self.device.name}. \n")
        except serial.SerialException as e:
            print("Error: ", e)

    def set_fs_settings(self, measurement_mode, measurement_channel, current_measurement_range, voltage_measurement_range = "1V"):
        # empty the stack
        self.device.write(bytearray([0xB0, 0x03, 0xFF, 0xFF, 0xFF, 0xB0]))

        settings = [0xB0, 0x04, int(input_user.check_measurement_mode(measurement_mode)),
                    input_user.check_measurement_channel(measurement_channel),
                    input_user.check_current_range_settings(current_measurement_range),
                    input_user.check_voltage_range_settings(voltage_measurement_range), 0xB0]

        if -1 in settings:
            print("Invalid Input for fs Settings. Using default settings")
            settings = [0xB0, 0x03, 0x02, 0x01, 0x00, 0xB0]

        self.device.write(bytearray(settings))
        print("Response ", self.device.read(4))
        print("Set the fs Settings.")

    def get_fs_settings(self):
        self.device.reset_input_buffer()
        self.device.write(bytearray([0xB1, 0x00, 0xB1]))

        response = self.device.read(32)  # reads 32 Bytes
        print("Raw response:", response.hex())

        # Search for valid B1-Frames (Start == 0xB1, End == 0xB1, Length == 6)
        for i in range(len(response) - 5):
            if response[i] == 0xB1 and response[i + 6] == 0xB1:
                frame = response[i:i + 7]
                print("B1-Frame found: ", frame.hex())
                mode, channel, current, voltage = frame[2:6]
                print(
                    f"measurement mode: 0x{mode:02X}, measurement channel: 0x{channel:02X}, "
                    f"current range settings: 0x{current:02X}, voltage range settings: 0x{voltage:02X}")
                return

        print("No valid B1 frame found.")
        print("\n")

    def set_setup(self, start_frequency, end_frequency, count, scale, precision, amplitude, excitation_type):
        # resets the setup
        self.device.write(bytearray([0x86, 0x01, 0x01, 0x86]))

        self.frequency_points = count

        settings = [
                    "Start: ", 0xB6, # Start
                    "Length: ", 0x16,  # Length
                    "Frequency List Option: ", 0x03, # Add Frequency List
                    "Start and Stop Frequency: ", input_user.check_frequency_range(start_frequency, end_frequency), #start and stop frequency
                    "Count: ", input_user.check_count(count), # count
                    "Scale: ", input_user.check_scale(scale), #scale
                    "Precision: ", input_user.check_precision(precision), #precision
                    "Amplitude: ", input_user.check_amplitude(amplitude, excitation_type) # amplitude

                    ]
        frequency_data = input_user.check_frequency_range(start_frequency, end_frequency)[0] + input_user.check_frequency_range(start_frequency, end_frequency)[1]

        settings_formatted = [0xB6, 0x16, 0x03]

        for data in frequency_data:
            settings_formatted.append(data)

        for data in input_user.check_count(count):
            settings_formatted.append(data)

        settings_formatted.append(input_user.check_scale(scale))

        for data in input_user.check_precision(precision):
            settings_formatted.append(data)

        for data in input_user.check_amplitude(amplitude, excitation_type):
            settings_formatted.append(data)

        settings_formatted.append(0xB6)

        print("Settings unformatted: ", settings)
        numbers_in_hex = [util.toHex(number) for number in settings_formatted]
        print("Numbers in hex: ", numbers_in_hex)
        print("Settings formatted in Setup: ", settings_formatted)


        self.device.write(bytearray(settings_formatted))
        print("Response for set Setup: ", self.device.read(4))

        print("Set the setup. \n")


    def start_measurement(self, cycles: int = 20):
        results = []

        if not self.device:
            print("Device not connected.")
            return results

        # Send measurement start command
        repeat_low = cycles & 0xFF
        repeat_high = (cycles >> 8) & 0xFF
        command = bytearray([0xB8, 0x03, 0x01, repeat_high, repeat_low, 0xB8])
        self.device.write(command)

        print(f"Started measurement for {cycles} cycles.")

        # Read results (frequency points per cycle × cycles total)
        num_points = self.frequency_points * cycles
        for _ in range(num_points):
            response = self.device.read(13)  # [CT] 0A [ID] [Real] [Imag] [CT]
            if len(response) == 0:
                print("Empty response.")
                continue

            if len(response) < 13:
                print(f"ACK received: {response.hex()}")
                continue

            """
            when time stamp and current range are disabled the response is 13 Bytes long
            0 : CT (Start)
            1 : LE
            2-3 : Frequency ID
            4-7: Real part
            8-11: imaginary part
            12: CT (End)
            """
            freq_id = int.from_bytes(response[2:4], byteorder='big')
            real = struct.unpack('>f', response[4:8])[0]
            imag = struct.unpack('>f', response[8:12])[0]
            results.append((freq_id, real, imag))

        # to stop measurement mode
        self.device.write(bytearray([0xB8, 0x01, 0x00, 0xB8]))

        #writes it in an CSV File (measurement_results.csv
        #overwrite the old one every time a new measurement is started
        with open('measurement_results.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frequency ID', 'Real Part', 'Imaginary Part'])  # Header
            writer.writerows(results)

        print("Measure data was saved in 'measurement_results.csv'. \n")

        return results
