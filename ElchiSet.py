import argparse
import datetime
import time

import yaml
from serial.serialutil import SerialException

from Drivers.ElchWorks import Thermolino, Thermoplatino, ElchLaser
from Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from Drivers.Jumo import JumoQuantol
from Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from Drivers.Omega import OmegaPt
from Drivers.Pyrometer import Pyrometer
from Drivers.ResistiveHeater import CeramicSputterHeater
from Drivers.TestDevices import TestSensor, TestController, NiceTestController

controller_types = {'Eurotherm2408': Eurotherm2408, 'Eurotherm3216': Eurotherm3216,
                    'Eurotherm3508': Eurotherm3508, 'Omega Pt': OmegaPt, 'Jumo Quantrol': JumoQuantol,
                    'Elch Laser Control': ElchLaser, 'Elch Heater Controller': ElchLaser,
                    'HCS34 (Experimental)': CeramicSputterHeater, 'Test Controller': TestController,
                    'Nice Test Controller': NiceTestController}
sensor_types = {'Pyrometer': Pyrometer, 'Thermolino': Thermolino, 'Thermoplatino': Thermoplatino,
                'Keithly2000 Temperature': Keithly2000Temp, 'Keithly2000 Voltage': Keithly2000Volt,
                'Eurotherm3508': Eurotherm3508S, 'Test Sensor': TestSensor}


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Example CLI application", fromfile_prefix_chars='+')

    parser.add_argument('config_path', type=str, help='Path to configuration file')
    parser.add_argument('-s', '--setpoint', type=str, help='Heater set point')
    parser.add_argument('-l', '--log_path', type=str, help='Log file path')
    parser.add_argument('-p', '--prog_path', type=str, help='')

    # Parse the arguments
    args = parser.parse_args()

    # Read the config file
    with open(args.config_path, 'r') as file:
        config = yaml.safe_load(file)

    if args.setpoint is not None:
        setpoint = float(args.setpoint)
    elif args.prog_path:
        with open(args.prog_path, 'r') as file:
            lines = file.readlines()
            if len(lines) > 0:
                setpoint = float(lines[0].rstrip())
                with open(args.prog_path, 'w') as file:
                    file.writelines(lines[1:])
            else:
                print('Program finished!')
                return
    else:
        input('Neither setpoint nor program given! Press ENTER to quit.')
        return

    print(f'Setting {config["type_heater"]} at {config["port_heater"]} to {setpoint} C.')
    print(f'Monitoring via {config["type_sensor"]} at {config["port_sensor"]}.')
    print(f'Wating until the Temperature changes by less than {config["delta_temp"]} C for {config["delta_time"]} s.')
    print('Starting in 5 seconds, press Ctrl+C or close window to abort.')
    for i in range(5):
        print(f'{5 - i} ...')
        time.sleep(1)

    # Connect devices
    try:
        controller = controller_types[config['type_heater']](portname=config['port_heater'], slaveadress=1)
        sensor = sensor_types[config['type_sensor']](port=config['port_sensor'])
    except SerialException:
        input('Serial connection error, press ENTER to quit.')
        return

    # Set the temeprature
    controller.set_target_setpoint(setpoint)
    if args.log_path:
        with open(args.log_path, 'a') as logfile:
            now = datetime.datetime.now(datetime.UTC)
            logfile.write(f'{int(now.timestamp())}, {now.strftime("%Y-%m-%d %H:%M:%S")} UTC, Set {setpoint:.2f} C\n')

    # Count down from delta_time to zero
    # Measure temeperature every time_res seconds
    # Reset if the temperature deviates by more than delta_temp
    time_left = float(config['delta_time'])
    last_measurement_time = time.time()
    last_meas_temp = sensor.get_sensor_value()
    while time_left > 0:
        if time.time() - last_measurement_time < float(config['time_res']):
            # Less than time_res seconds have passed since the last measurement, do nothing
            continue

        last_measurement_time = time.time()
        current_temp = sensor.get_sensor_value()
        print(f'Current temeprature: {current_temp:.2f}')
        if abs(current_temp - last_meas_temp) > float(config['delta_temp']):
            # Temeprature varies by more than delta_temp
            # Reset the coundown and set the current temperature as reference for constancy
            time_left = float(config['delta_time'])
            last_meas_temp = sensor.get_sensor_value()
        else:
            # Temperature stays within delta_temp, decrease remaining time by time_res
            time_left -= float(config['time_res'])
        print(f'Time left: {time_left}')

    if args.log_path:
        with open(args.log_path, 'a') as logfile:
            now = datetime.datetime.now(datetime.UTC)
            logfile.write(f'{int(now.timestamp())}, {now.strftime("%Y-%m-%d %H:%M:%S")} UTC, {last_meas_temp:.2f} C\n')


if __name__ == '__main__':
    main()