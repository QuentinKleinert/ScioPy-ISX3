from src.ISX3 import ISX3

isx3 = ISX3(n_el=4)
isx3.connect_device_FS(port="COM3") # change to com port if necessary

isx3.set_fs_settings()
isx3.get_fs_settings()