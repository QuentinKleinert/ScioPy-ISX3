import struct
import serial
import serial.tools.list_ports
import csv


class ISX3:
    def __init__(self, n_el: int) -> None:
        self.n_el = n_el
        self.serial_protocol = None
        self.device = None

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
            print("Connection to", self.device.name, "is established.")
        except serial.SerialException as e:
            print("Error: ", e)

    def get_fs_settings(self):
        self.device.reset_input_buffer()
        self.device.write(bytearray([0xB1, 0x00, 0xB1]))

        response = self.device.read(32)  #reads 32 Bytes
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

    def set_fs_settings(self):
        # empty the stack
        self.device.write(bytearray([0xB0, 0x03, 0xFF, 0xFF, 0xFF, 0xB0]))
        # set the measurement channel to Main Port / BNC Channel
        self.device.write(bytearray([0xB0, 0x03, 0x02, 0x01, 0x00, 0xB0]))
        print("Set the fs Settings.")

    """
    B6                // [CT] Control Token - Start of command
    16                // [LE] Length of command data: 22 bytes follow
    03                // [OB] Operation Byte: 0x03 = Add frequency list
    
    44 7A 00 00       // [CD] Start frequency = 1000.0 Hz (float)
                      // → Sets the beginning of the frequency sweep
    
    4B 18 96 80       // Stop frequency = 10,000,000.0 Hz (float)
                      // → Sets the end of the frequency sweep
    
    42 F0 00 00       // Count = 60.0 (float)
                      // → Sets how many frequency points will be used in the sweep
    
    01                // Scale = 0x01
                      // → 0x00 = linear scale, 0x01 = logarithmic scale
    
    3F 80 00 00       // Precision = 1.0 (float)
                      // → Defines the measurement precision/resolution
    
    3D CC CC CD       // Amplitude = 0.1 V (float)
                      // → Peak excitation voltage to use for each frequency point
    
    B6                // [CT] Control Token - End of command

    """
    def set_setup(self):
        #sets up the setup
        self.device.write(bytearray([0xB6, 0x16, 0x03, 0x44, 0x7A, 0x00, 0x00, 0x4B, 0x18, 0x96, 0x80, 0x42, 0xF0, 0x00,
                                     0x00, 0x01, 0x3F, 0x80, 0x00, 0x00, 0x3D, 0xCC, 0xCC, 0xCD, 0xB6]))

        print("Set the setup.")

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

        # Read results (assumes 60 frequency points per cycle × cycles total)
        num_points = 60 * cycles
        for _ in range(num_points):
            response = self.device.read(13)  # [CT] 0A [ID] [Real] [Imag] [CT] = 13 Bytes

            freq_id = int.from_bytes(response[2:4], byteorder='big')
            real = struct.unpack('>f', response[4:8])[0]
            imag = struct.unpack('>f', response[8:12])[0]
            results.append((freq_id, real, imag))

        # to stop measurement mode
        self.device.write(bytearray([0xB8, 0x01, 0x00, 0xB8]))

        with open('measurement_results.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frequency ID', 'Real Part', 'Imaginary Part'])  # Header
            writer.writerows(results)

        print("Measure data was saved in 'measurement_results.csv'.")

        return results


