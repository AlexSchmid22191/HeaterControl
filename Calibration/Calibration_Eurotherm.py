import time
import datetime
import minimalmodbus

power_min = 30
power_max = 90
power_step = 5
step_time = 3600
data_interval = 1
euro_port = 'COM10'
logfile_path = 'Calibration_Eurotherm.csv'

set_powers = list(range(power_min, power_max + power_step, power_step)) + \
             list(range(power_max - power_step, power_min - power_step, -power_step)) + \
             [0]

with open(logfile_path, 'w') as logfile:
    logfile.write('# PLD Calibration - eurotherm readout\n')
    logfile.write('# unixtime (s), temperature (°C)')

euro = minimalmodbus.Instrument(euro_port, slaveaddress=1)
euro.serial.baudrate = 9600

euro.write_register(273, 1)

last_unix_time = 0

for set_power in set_powers:
    # Set output power
    euro.write_register(3, set_power, number_of_decimals=1)
    power = euro.read_register(3, 1)
    print(f'{datetime.datetime.now()}: Set power to {power}')

    with open(logfile_path, 'a') as logfile:
        logfile.write(f'{datetime.datetime.now()}: Set power to {power}')

    # Read data
    step_start_time = time.time()
    last_measurement = time.time()
    while (current_time := time.time()) - step_start_time < step_time:
        if current_time - last_measurement > data_interval:
            temperature = euro.read_register(1, number_of_decimals=0)
            print(f'{datetime.datetime.now()}, {temperature}')
            with open(logfile_path, 'a') as logfile:
                logfile.write(f'{time.time(), temperature}\n')
