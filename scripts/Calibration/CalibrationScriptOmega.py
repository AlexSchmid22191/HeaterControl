import time
from src.Drivers.Pyrometer import Pyrometer
from src.Drivers.Omega import OmegaPt

pyro = Pyrometer('COM3')
omega = OmegaPt('COM10', 1)

t_step = -1
last_unix_time = 0

target_temperatures = list(range(200, 1050, 50)) + list(range(950, 150, -50))

omega.set_rate(30)

while t_step < len(target_temperatures):
    success = False
    while not success:
        try:
            temp = pyro.get_sensor_value()
            tc_temp = omega.get_process_variable()
            success = True
        except:
            omega.serial.close()
            omega.serial.open()
            tc_temp = omega.get_process_variable()
            temp = pyro.get_sensor_value()
            time.sleep(0.2)

    unixtime = float(time.time())

    if (unixtime - last_unix_time) > 1800:
        last_unix_time = unixtime
        t_step += 1

        try:
            omega.set_target_setpoint(target_temperatures[t_step])
        except:
            time.sleep(0.05)
            omega.set_target_setpoint(target_temperatures[t_step])

        print('Changing Output power to {:f}'.format(target_temperatures[t_step]))
        with open('Logfile_Switching.txt', 'a') as logfile:
            logfile.write('Time: {:f} - Changing Output power to {:f}\n'.format(unixtime, target_temperatures[t_step]))
        with open('Logfile_{:d}_{:s}.txt'.format(target_temperatures[t_step], 'Up' if t_step <= int(len(target_temperatures)/2)
                  else 'Down'), 'a') as logfile:
            logfile.write('Unixtime (s), Pyrometer temperature (°C), TC temperature (°C)\n')

    print('Unixtime: {:f}, Pyrometer temperature: {:f}, TC temperature: {:f}'.format(unixtime, temp, tc_temp))

    with open('Logfile_{:d}_{:s}.txt'.format(target_temperatures[t_step], 'Up' if t_step <= int(len(target_temperatures)/2)
              else 'Down'), 'a') as logfile:
        logfile.write('{:f},{:f},{:f}\n'.format(unixtime, temp, tc_temp))

    time.sleep(0.5)
