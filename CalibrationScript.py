import time
import serial
import datetime
import minimalmodbus
from Drivers.Pyrometer import Pyrometer
from Drivers.Eurotherms import Eurotherm2408


power_min = 30
power_max = 90
power_step = 5

step_time = 3600

com_pyro = 'COM5'
com_euro = 'COM10'

file_path = 'Logfile.txt'

with open(file_path, 'w') as logfile:
    logfile.write('# Calibration Script\n')
    logfile.write('# unixtime, Eurotherm Temperature (°C), Pyrometer Temperatur (°C)\n')

set_powers = list(range(power_min, power_max+power_step, power_step)) + \
             list(range(power_max-power_step, power_min-power_step, -power_step))

pyro = Pyrometer(com_pyro)
euro = Eurotherm2408(com_euro, 1)
euro.set_manual_mode()

last_unix_time = 0
errorcount = 0

for set_power in set_powers:

    # Set output power
    sucess = False
    while not sucess:
        try:
            euro.set_manual_output_power(set_power)
            sucess = euro.read_register(3, 1) == set_power
        except (serial.SerialException, minimalmodbus.ModbusException) as error:
            time.sleep(0.1)
            errorcount += 1
        if errorcount > 5:
            errorcount = 0
            print('Serial connection error! Reconnecting..', end='')
            euro.serial.close()
            time.sleep(3)
            print('.', end='')
            euro.serial.open()
            time.sleep(3)
            print('.')

    with open(file_path, 'a') as logfile:
        logfile.write('\nChanging Output power to {:3.1f}\n\n'.format(set_power))

    # Read data
    errorcount = 0
    step_start_time = time.time()
    while (current_time := time.time()) - step_start_time < step_time:
        sucess = False
        while not sucess:
            try:
                t_pyro = pyro.get_sensor_value()
                t_euro = euro.get_process_variable()
                sucess = True
                print(f'{current_time:.3f}, {t_euro:3.1f}, {t_pyro:3.1f}')
                with open(file_path, 'a') as logfile:
                    logfile.write(f'{current_time:.3f}, {t_euro:3.1f}, {t_pyro:3.1f}\n')
            except (serial.SerialException, minimalmodbus.ModbusException, ValueError) as error:
                time.sleep(0.1)
                errorcount += 1

            if errorcount > 5:
                errorcount = 0
                print('Serial connection error! Reconnecting..', end='')
                euro.serial.close()
                pyro.close()
                time.sleep(3)
                print('.', end='')
                euro.serial.open()
                pyro.open()
                time.sleep(3)
                print('.')
        time.sleep(0.25)
