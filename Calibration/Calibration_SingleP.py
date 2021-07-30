import time
import serial
import datetime
import minimalmodbus
from Drivers.Pyrometer import Pyrometer
from Drivers.Eurotherms import Eurotherm2408

power = 30
run_time = 3600

com_pyro = 'COM2'
com_euro = 'COM10'

file_path = f'Logfile_{power}_up.txt'

with open(file_path, 'w') as logfile:
    logfile.write(f'# Calibration Script - Power: {power}\n')
    logfile.write('# unixtime, Eurotherm Temperature (°C), Pyrometer Temperatur (°C)\n')

pyro = Pyrometer(com_pyro)
euro = Eurotherm2408(com_euro, 1)
time.sleep(1)

euro.set_manual_mode()
euro.set_manual_output_power(power)
print(f'Power set to: {euro.read_register(3, 1)}')

start_time = time.time()
last_measured_pyro = time.time()
last_measured_euro = time.time()

while (current_time := time.time()) - start_time < run_time:
    if current_time - last_measured_pyro > 0.25:
        try:
            t_pyro = pyro.get_sensor_value()
            last_measured_pyro = time.time()
        except:
            t_pyro = None
    if current_time - last_measured_euro > 1:
        try:
            t_euro = euro.get_process_variable()
            last_measured_euro = time.time()
        except:
            t_euro = None

        print(f'{current_time:.3f}, {t_euro:3.1f}, {t_pyro:3.1f}')
        with open(file_path, 'a') as logfile:
            logfile.write(f'{current_time:.3f}, {t_euro:3.1f}, {t_pyro:3.1f}\n')
