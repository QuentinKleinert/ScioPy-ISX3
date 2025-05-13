
import serial
import serial.tools.list_ports


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
            print(f"Connected to {self.device.name}.")
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

