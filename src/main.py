from src.ISX3 import ISX3

isx3 = ISX3(n_el=4)
isx3.connect_device_FS(port="COM3") # change to com port if necessary

#Sets up measurement mode, measurement Channel (MAIN PORT etc.) and range settings
isx3.set_fs_settings([0xB0, 0x03, 0x02, 0x01, 0x00, 0xB0])
isx3.get_fs_settings()



"""
    B6                // [CT] Control Token - Start of command
    16                // [LE] Length of command data: 22 bytes follow to next B6
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
isx3.set_setup([0xB6, 0x16, 0x03, 0x44, 0x7A, 0x00, 0x00, 0x4B, 0x18, 0x96, 0x80, 0x42, 0xF0, 0x00, 0x00, 0x01, 0x3F,
                0x80, 0x00, 0x00, 0x3D, 0xCC, 0xCC, 0xCD, 0xB6])


#starts and stops the measurement, add more or less cycles if necessary
results = isx3.start_measurement(cycles=20)
print(results)
