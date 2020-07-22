import time
from Drivers.Pyrometer import Pyrometer
from Drivers.Eurotherms import Eurotherm2408


pyro = Pyrometer('COM3')
euro = Eurotherm2408('COM10', 1)

t_step = 0
last_unix_time = 0

output_powers = list(range(20, 105, 5)) + list(range(95, 15, -5))

euro.set_manual_mode()

while True:
    temp = pyro.read_temperature()
    unixtime = time.time()

    print('Unixtime: {:.3f}, Temp: {:3.2f}\n'.format(time, temp))

    with open('Logfile.txt', 'a') as logfile:
        logfile.write('Unixtime: {:.3f}, Temp: {:3.2f}\n'.format(time, temp))

    if (unixtime - last_unix_time) > 1800:
        last_unix_time = unixtime
        euro.set_manual_output_power(output_powers[t_step])
        print('Changing Output power to {:3.1f}'.format(output_powers[t_step]))
        with open('Logfile.txt', 'a') as logfile:
            logfile.write('\nChanging Output power to {:3.1f}\n\n'.format(output_powers[t_step]))
        t_step += 1

    time.sleep(0.1)
