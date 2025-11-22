import sys
import time
import datetime
from typing import Dict
from pathlib import Path


import yaml
from serial.serialutil import SerialException

from src.Drivers.BaseClasses import AbstractSensor, AbstractController
from src.Drivers.ElchWorks import Thermolino, Thermoplatino, ElchLaser
from src.Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from src.Drivers.Jumo import JumoQuantol
from src.Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from src.Drivers.Omega import OmegaPt
from src.Drivers.Pyrometer import Pyrometer
from src.Drivers.ResistiveHeater import ResistiveHeaterHCS, ResistiveHeaterTenma
from src.Drivers.TestDevices import TestSensor, TestController, NiceTestController


controller_types = {'Eurotherm2408': Eurotherm2408, 'Eurotherm3216': Eurotherm3216,
                    'Eurotherm3508': Eurotherm3508, 'Omega Pt': OmegaPt, 'Jumo Quantrol': JumoQuantol,
                    'Elch Laser Control': ElchLaser, 'Elch Heater Controller': ElchLaser,
                    'Resistive Heater Tenma': ResistiveHeaterTenma, 'Resistive Heater HCS': ResistiveHeaterHCS,
                    'Test Controller': TestController, 'Nice Test Controller': NiceTestController}
sensor_types = {'Pyrometer': Pyrometer, 'Thermolino': Thermolino, 'Thermoplatino': Thermoplatino,
                'Keithly2000 Temperature': Keithly2000Temp, 'Keithly2000 Voltage': Keithly2000Volt,
                'Eurotherm3508': Eurotherm3508S, 'Test Sensor': TestSensor}


def delayed_exit(message: str, error_code=0):
    print(message)
    print('Press enter to exit!')
    input()
    sys.exit(error_code)


def load_config(config_path: str | Path) -> Dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        delayed_exit(f'Error: Config file not found: {config_path}', 1)
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {config_path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {config_path}: {e}', 1)
    if not isinstance(config, dict):
        delayed_exit('Error: Invalid config format!')

    print(f'I read the following configuration from {config_path}:')
    for k, v in config.items():
        print(f"{k}: {v}")

    return config


def validate_config(config: dict) -> None:
    required = {'type_heater', 'port_heater', 'type_sensor', 'port_sensor', 'delta_temp', 'delta_time', 'time_res'}
    missing = required - config.keys()
    if missing:
        delayed_exit(f'Missing entries in config file: {missing}!', 1)

    for key in ['delta_temp', 'delta_time', 'time_res']:
        try:
            config[key] = float(config[key])
        except ValueError as e:
            delayed_exit(f'Error converting value of {config[key]} for {key}: {e}', 1)

    if config['type_heater'] not in controller_types:
        delayed_exit(f'Invalid heater type encountered: {config["type_heater"]}!\n'
                     f' Valid heater types: {", ".join(controller_types.keys())}', 1)

    if config['type_sensor'] not in sensor_types:
        delayed_exit(f'Invalid sensor type encountered: {config["type_sensor"]}!\n'
                     f' Valid sensor types: {", ".join(sensor_types.keys())}', 1)

    print('Config validation successful!')


def connect_devices(config: dict) -> tuple[AbstractController, AbstractSensor]:
    controller, sensor = None, None
    try:
        controller = controller_types[config['type_heater']](portname=config['port_heater'], slaveadress=1)
    except SerialException:
        delayed_exit(f'Error connecting heater at {config["port_heater"]}!')
    else:
        print('Heater connection successful!')

    try:
        sensor = sensor_types[config['type_sensor']](port=config['port_sensor'])
    except SerialException:
        delayed_exit(f'Error connecting sensor at {config["port_sensor"]}!')
    else:
        print('Sensor connection successful!')

    return controller, sensor


def temperature_control_loop(setpoint: float, config: dict, log_path: str | Path) -> None:
    controller, sensor = connect_devices(config)

    print(f'Setting {config["type_heater"]} at {config["port_heater"]} to {setpoint} C!')
    print(f'Monitoring via {config["type_sensor"]} at {config["port_sensor"]}!')
    print(f'Waiting until the Temperature changes by less than {config["delta_temp"]} C for {config["delta_time"]} s!')
    print('Starting in 5 seconds, press Ctrl+C or close window to abort!')
    for i in range(5):
        print(f'{5 - i} ...')
        time.sleep(1)

    try:
        controller.set_target_setpoint(setpoint)
    except (SerialException, ValueError) as e:
        delayed_exit(f'Error setting the temperature: {e}')
    else:
        try:
            with open(log_path, 'a') as logfile:
                now = datetime.datetime.now(datetime.timezone.utc)
                logfile.write(f'{int(now.timestamp())}, {now.strftime("%Y-%m-%d %H:%M:%S")} UTC, Set: {setpoint:.2f} C\n')
        except PermissionError:
            delayed_exit(f'Error: Permission denied writing {log_path}', 1)
        except OSError as e:
            delayed_exit(f'Error writing {log_path}: {e}', 1)

    # Count down from delta_time to zero
    # Measure temperature every time_res seconds
    # Reset if the temperature deviates by more than delta_temp
    last_meas_temp, current_temp = None, None
    time_left = config['delta_time']
    last_measurement_time = time.time()
    try:
        last_meas_temp = sensor.get_sensor_value()
    except (SerialException, ValueError) as e:
        delayed_exit(f'Error reading the sensor value: {e}')

    while time_left > 0:
        if time.time() - last_measurement_time < config['time_res']:
            # Less than time_res seconds have passed since the last measurement, do nothing for one second
            time.sleep(1)
            continue

        try:
            current_temp = sensor.get_sensor_value()
            last_measurement_time = time.time()
            print(f'Current temperature: {current_temp:.2f}')
        except (SerialException, ValueError) as e:
            delayed_exit(f'Error reading the sensor value: {e}')

        if abs(current_temp - last_meas_temp) > config['delta_temp']:
            # Temperature varies by more than delta_temp
            # Reset the countdown and set the current temperature as reference for constancy
            last_meas_temp = current_temp
            time_left = config['delta_time']
            print(f'Temperature changed by more than {config["delta_temp"]}, resetting countdown!')
        else:
            # Temperature stays within delta_temp, decrease remaining time by time_res
            time_left -= config['time_res']
        print(f'Time left: {time_left} s')

    try:
        with open(log_path, 'a') as logfile:
            now = datetime.datetime.now(datetime.timezone.utc)
            logfile.write(f'{int(now.timestamp())}, {now.strftime("%Y-%m-%d %H:%M:%S")} UTC, Is: {current_temp:.2f} C\n')
    except PermissionError:
        delayed_exit(f'Error: Permission denied writing: {log_path}', 1)
    except OSError as e:
        delayed_exit(f'Error writing {log_path}: {e}', 1)

    print('Temperature control loop finished!')
