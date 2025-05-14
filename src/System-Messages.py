
Generale_System_Messages = {
    [0x18, 0x01, 0x01, 0x18]: "Frame-Not-Acknowledge: Incorrect syntax",
    [0x18, 0x01, 0x02, 0x18]: "Timeout: Communication-timeout (less data than expected)",
    [0x18, 0x01, 0x04, 0x18]: "Wake-Up Message: System boot ready",
    [0x18, 0x01, 0x11, 0x18]: "TCP-Socket: Valid TCP client-socket connection",
    [0x18, 0x01, 0x81, 0x18]: "Not-Acknowledge: Command has not been executed",
    [0x18, 0x01, 0x82, 0x18]: "Not-Acknowledge: Command could not be recognized",
    [0x18, 0x01, 0x83, 0x18]: "Command-Acknowledge: Command has been executed successfully",
    [0x18, 0x01, 0x84, 0x18]: "System-Ready Message: System is operational and ready to receive data",
}

Device_Specific_System_Messages = {
    [0x18, 0x01, 0x90, 0x18]: "Overcurrent Detected Value of DC current on W-ports exceeds capability of configured current range",
    [0x18, 0x01, 0x91, 0x18]: "Overvoltage Detected Value of DC voltage difference between R and WS port exceeds capability of configured voltage range",
}