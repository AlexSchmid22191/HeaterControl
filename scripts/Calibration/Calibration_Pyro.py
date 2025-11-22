import datetime
import time

import serial

pyro_port = 'COM2'
data_interval = 100  # ms
logfile_path = 'Calibration_Pyrometer.csv'

with open(logfile_path, 'w') as logfile:
    logfile.write('# PLD Calibration - Pyrometer readout\n')
    logfile.write('# unixtime (s), temperature (°C)')

x = serial.Serial(pyro_port)
time.sleep(2)
x.write(f'TRIG ON {data_interval}\r'.encode())

while True:
    answer = x.read_until(b'\r').decode()
    temperature = float(answer.split(' ')[0])
    print(f'{datetime.datetime.now()}, {answer}')
    with open(logfile_path, 'a') as logfile:
        logfile.write(f'{time.time(), temperature}\n')
