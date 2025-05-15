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
            print(f"Successfully Connected to {self.device.name}. \n")
        except serial.SerialException as e:
            print("Error: ", e)

    def set_fs_settings(self, measurement_mode, measurement_channel="Main Port",
                        current_measurement_range="autoranging", voltage_measurement_range="1V"):
        # Clear stack to avoid overflow
        self.device.write(bytearray([0xB0, 0x03, 0xFF, 0xFF, 0xFF, 0xB0]))

        # Convert parameters
        mode = input_user.check_measurement_mode(measurement_mode)
        current_range = input_user.check_current_range_settings(current_measurement_range)
        voltage_range = input_user.check_voltage_range_settings(voltage_measurement_range)
        channel_code = input_user.check_measurement_channel(measurement_channel)

        if -1 in [mode, current_range, voltage_range, channel_code]:
            print("Invalid input detected. Aborting.")
            return

        # 2-byte extension channels (default to 0x0000 if not used)
        ext = [0x00, 0x00]

        # Build command based on measurement mode
        if mode == 0x01:  # 2-point
            command = [
                0xB0, 0x09, mode, current_range, voltage_range,
                channel_code, *ext,  # C channel
                channel_code, *ext,  # W channel
                0xB0
            ]
        elif mode == 0x03:  # 3-point
            command = [
                0xB0, 0x0C, mode, current_range, voltage_range,
                channel_code, *ext,  # C channel
                channel_code, *ext,  # R channel
                channel_code, *ext,  # W channel
                0xB0
            ]
        elif mode == 0x02:  # 4-point
            command = [
                0xB0, 0x0F, mode, current_range, voltage_range,
                channel_code, *ext,  # C channel
                channel_code, *ext,  # R channel
                channel_code, *ext,  # S channel
                channel_code, *ext,  # W channel
                0xB0
            ]
        else:
            print("Unsupported measurement mode. Aborting.")
            return

        self.device.write(bytearray(command))
        response = self.device.read(4)
        print("Response from device: ", response)
        print("FS settings applied.\n")

    def get_fs_settings(self):
        self.device.reset_input_buffer()

        # Step 1: Query number of configured channels
        request = bytearray([0xB1, 0x03, 0x02, 0x00, 0xB1])
        self.device.write(request)
        response = self.device.read(16)

        print("Channel count response:", response.hex())

        if len(response) < 6 or response[0] != 0xB1 or response[-1] != 0xB1:
            print("No valid B1 response frame for channel count.\n")
            return

        num_channels = int.from_bytes(response[2:4], 'big')
        print(f"Number of configured channels: {num_channels}")

        if num_channels == 0:
            print("No configured frontend channels.\n")
            return

        # Step 2: Query each channel config
        for ch in range(1, num_channels + 1):
            self.device.reset_input_buffer()
            self.device.write(bytearray([0xB1, 0x02, ch, 0xB1]))
            response = self.device.read(32)

            print(f"\nRaw response for channel {ch}:", response.hex())

            for i in range(len(response)):
                if response[i] == 0xB1:
                    end_index = response.find(b'\xB1', i + 1)
                    if end_index != -1:
                        frame = response[i:end_index + 1]
                        print("Valid B1 Frame found:", frame.hex())

                        frame_type = frame[1]
                        mode = frame[2]
                        current = frame[3]
                        voltage = frame[4]

                        def get_channel_info(start_index):
                            ch = frame[start_index]
                            ext = int.from_bytes(frame[start_index + 1:start_index + 3], 'big')
                            print("\n")
                            return ch, ext

                        if frame_type == 0x09 and len(frame) == 17:  # 2-point
                            ch_c, ext_c = get_channel_info(5)
                            ch_w, ext_w = get_channel_info(8)
                            print("2-point configuration:")
                            print(f"Mode: 0x{mode:02X}, Current: 0x{current:02X}, Voltage: 0x{voltage:02X}")
                            print(f"C: 0x{ch_c:02X} (ext: {ext_c}), W: 0x{ch_w:02X} (ext: {ext_w})")

                        elif frame_type == 0x0C and len(frame) == 20:  # 3-point
                            ch_c, ext_c = get_channel_info(5)
                            ch_r, ext_r = get_channel_info(8)
                            ch_w, ext_w = get_channel_info(11)
                            print("3-point configuration:")
                            print(f"Mode: 0x{mode:02X}, Current: 0x{current:02X}, Voltage: 0x{voltage:02X}")
                            print(
                                f"C: 0x{ch_c:02X} (ext: {ext_c}), R: 0x{ch_r:02X} (ext: {ext_r}), W: 0x{ch_w:02X} (ext: {ext_w})")

                        elif frame_type == 0x0F and len(frame) == 23:  # 4-point
                            ch_c, ext_c = get_channel_info(5)
                            ch_r, ext_r = get_channel_info(8)
                            ch_s, ext_s = get_channel_info(11)
                            ch_w, ext_w = get_channel_info(14)
                            print("4-point configuration:")
                            print(f"Mode: 0x{mode:02X}, Current: 0x{current:02X}, Voltage: 0x{voltage:02X}")
                            print(f"C: 0x{ch_c:02X} (ext: {ext_c}), R: 0x{ch_r:02X} (ext: {ext_r}), "
                                  f"S: 0x{ch_s:02X} (ext: {ext_s}), W: 0x{ch_w:02X} (ext: {ext_w})")
                        else:
                            print("Unknown or unsupported frame format.")
                        break
            else:
                print("No valid B1 frame found for this channel.")
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

    def get_setup(self):
        pass

    def start_measurement(self, spectres: int = 20):
        results = []

        spectres = input_user.check_input_spectres(spectres)

        if not self.device:
            print("Device not connected.")
            return results

        command = bytearray([0xB8, 0x03, 0x01, 0x00, spectres, 0xB8])
        # [CT] Start, [LE] Length, [OB] Operation (Start/Stop), [CD], [CT] End
        self.device.write(command)

        print(f"Started measurement for {spectres} cycles.")

        num_points = self.frequency_points * spectres

        for _ in range(num_points):

            start_byte = b''
            while start_byte != b'\xB8':
                start_byte = self.device.read(1)
                if not start_byte:
                    print("Timeout waiting for start byte.")
                    continue


            header = self.device.read(1)
            if not header:
                print("Missing header byte.")
                continue

            frame_type = header[0]
            frame_lengths = {
                0x0A: 13,
                0x0B: 14,
                0x0E: 17,
                0x0F: 19
            }

            expected_length = frame_lengths.get(frame_type, 13) - 2
            rest = self.device.read(expected_length)
            if len(rest) != expected_length:
                print("Incomplete frame received.")
                continue

            frame = start_byte + header + rest
            print("Received Frame:", frame.hex())

            freq_id = int.from_bytes(frame[2:4], 'big')
            print(f"Frequency ID received: {freq_id}")
            real, imag = None, None
            timestamp = None
            current_range = None

            if frame_type == 0x0A:
                real = struct.unpack(">f", frame[4:8])[0]
                imag = struct.unpack(">f", frame[8:12])[0]
            elif frame_type == 0x0B:
                current_range = frame[4]
                real = struct.unpack(">f", frame[5:9])[0]
                imag = struct.unpack(">f", frame[9:13])[0]
            elif frame_type == 0x0E:
                timestamp = int.from_bytes(frame[4:8], 'big')
                real = struct.unpack(">f", frame[8:12])[0]
                imag = struct.unpack(">f", frame[12:16])[0]
            elif frame_type == 0x0F:
                timestamp = int.from_bytes(frame[4:8], 'big')
                current_range = frame[8]
                real = struct.unpack(">f", frame[9:13])[0]
                imag = struct.unpack(">f", frame[13:17])[0]
            else:
                print("Unrecognized frame type.")
                continue

            results.append((freq_id, real, imag, timestamp, current_range))

        # Stop measurement
        self.device.write(bytearray([0xB8, 0x01, 0x00, 0xB8]))

        # Write to CSV
        with open('measurement_results.csv', mode='w', newline='') as file:
            writer = csv.writer(file)

            # Determine header
            header = ['Frequency ID', 'Real Part', 'Imaginary Part']
            if any(r[3] is not None for r in results):
                header.append('Timestamp')
            if any(r[4] is not None for r in results):
                header.append('Current Range')
            writer.writerow(header)

            # Write each row
            for r in results:
                row = [r[0], r[1], r[2]]
                if 'Timestamp' in header:
                    row.append(r[3] if r[3] is not None else '')
                if 'Current Range' in header:
                    row.append(r[4] if r[4] is not None else '')
                writer.writerow(row)

        print("Measurement data saved to 'measurement_results.csv'.\n")
        print("Result Array: ", results)
        return results



