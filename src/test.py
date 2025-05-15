import check_User_Input as input_user

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
    amplitude="0.25V",
    excitation_type="voltage"
)

