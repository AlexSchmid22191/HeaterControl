import argparse
import datetime
import sys
import time

import yaml
from serial.serialutil import SerialException

from Drivers.AbstractSensorController import AbstractSensor, AbstractController
from Drivers.ElchWorks import Thermolino, Thermoplatino, ElchLaser
from Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from Drivers.Jumo import JumoQuantol
from Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from Drivers.Omega import OmegaPt
from Drivers.Pyrometer import Pyrometer
from Drivers.ResistiveHeater import ResistiveHeaterHCS, ResistiveHeaterTenma
from Drivers.TestDevices import TestSensor, TestController, NiceTestController

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


def read_lines(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        delayed_exit(f'Error: File not found: {path}', 1)
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {path}: {e}', 1)


def write_lines(path: str, lines):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except PermissionError:
        delayed_exit(f'Error: permission denied writing: {path}', 1)
    except OSError as e:
        delayed_exit(f'Error writing {path}: {e}', 1)


def find_first_unprocessed(lines):
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.endswith("-Processed"):
            continue
        return i
    return None


def mark_processed(line: str) -> str:
    return f'{line.strip()}-Processed\n' if not line.endswith('-Processed\n') else line


def get_setpoint_from_prog(filepath) -> float:
    lines = read_lines(filepath)
    idx = find_first_unprocessed(lines)
    if idx is None:
        delayed_exit('All entries in program file processed!', 0)

    raw = lines[idx].strip()
    try:
        setpoint = float(raw)
    except ValueError as e:
        delayed_exit(f'Error converting setpoint {raw!r}: {e}', 1)
    else:
        lines[idx] = mark_processed(lines[idx])
        write_lines(filepath, lines)
        return setpoint


def connect_devices(config: dict) -> tuple[AbstractController, AbstractSensor]:
    controller, sensor = None, None
    try:
        controller = controller_types[config['type_heater']](portname=config['port_heater'], slaveadress=1)
    except KeyError:
        delayed_exit(f'Invalid heater type encountered: {config["type_heater"]}!\n'
                     f' Valid heater types: {", ".join(controller_types.keys())}')
    except SerialException:
        delayed_exit(f'Error connecting heater at {config["port_heater"]}!')
    else:
        print('Heater connection successful!')

    try:
        sensor = sensor_types[config['type_sensor']](port=config['port_sensor'])
    except KeyError:
        delayed_exit(f'Invalid sensor type encountered: {config["type_sensor"]}!\n'
                     f' Valid sensor types: {", ".join(sensor_types.keys())}')
    except SerialException:
        delayed_exit(f'Error connecting sensor at {config["port_sensor"]}!')
    else:
        print('Sensor connection successful!')

    return controller, sensor


def temperature_control_loop(setpoint: float, config: dict, log_path=None) -> None:
    delta_time, time_res, delta_temp, time_left = None, None, None, None
    try:
        delta_time = float(config['delta_time'])
    except ValueError as e:
        delayed_exit(f'Error converting delta time: {config["delta_time"]}: {e}', 1)
    try:
        time_res = float(config['time_res'])
    except ValueError as e:
        delayed_exit(f'Error converting time res: {config["time_res"]}: {e}', 1)
    try:
        delta_temp = float(config['delta_temp'])
    except ValueError as e:
        delayed_exit(f'Error converting delta temp: {config["delta_temp"]}: {e}', 1)

    controller, sensor = connect_devices(config)

    print(f'Setting {config["type_heater"]} at {config["port_heater"]} to {setpoint} C!')
    print(f'Monitoring via {config["type_sensor"]} at {config["port_sensor"]}!')
    print(f'Waiting until the Temperature changes by less than {delta_temp} C for {delta_time} s!')
    print('Starting in 5 seconds, press Ctrl+C or close window to abort!')
    for i in range(5):
        print(f'{5 - i} ...')
        time.sleep(1)

    try:
        controller.set_target_setpoint(setpoint)
    except (SerialException, ValueError) as e:
        delayed_exit(f'Error setting the temperature: {e}')
    else:
        if log_path is not None:
            try:
                with open(log_path, 'a') as logfile:
                    now = datetime.datetime.now(datetime.timezone.utc)
                    logfile.write(f'{int(now.timestamp())}, {now.strftime("%Y-%m-%d %H:%M:%S")} UTC, Set {setpoint:.2f} C\n')
            except PermissionError:
                delayed_exit(f'Error: permission denied writing: {log_path}', 1)
            except OSError as e:
                delayed_exit(f'Error writing {log_path}: {e}', 1)

    # Count down from delta_time to zero
    # Measure temperature every time_res seconds
    # Reset if the temperature deviates by more than delta_temp
    last_meas_temp, current_temp = None, None
    time_left = delta_time
    last_measurement_time = time.time()
    try:
        last_meas_temp = sensor.get_sensor_value()
    except (SerialException, ValueError) as e:
        delayed_exit(f'Error reading the sensor value: {e}')

    while time_left > 0:
        if time.time() - last_measurement_time < time_res:
            # Less than time_res seconds have passed since the last measurement, do nothing for one second
            time.sleep(1)
            continue

        last_measurement_time = time.time()
        try:
            current_temp = sensor.get_sensor_value()
            print(f'Current temperature: {current_temp:.2f}')
        except (SerialException, ValueError) as e:
            delayed_exit(f'Error reading the sensor value: {e}')

        if abs(current_temp - last_meas_temp) > delta_temp:
            # Temperature varies by more than delta_temp
            # Reset the countdown and set the current temperature as reference for constancy
            last_meas_temp = current_temp
            time_left = delta_time
        else:
            # Temperature stays within delta_temp, decrease remaining time by time_res
            time_left -= time_res
        print(f'Time left: {time_left} s')

    if log_path is not None:
        try:
            with open(log_path, 'a') as logfile:
                now = datetime.datetime.now(datetime.timezone.utc)
                logfile.write(f'{int(now.timestamp())}, {now.strftime("%Y-%m-%d %H:%M:%S")} UTC, {current_temp:.2f} C\n')
        except PermissionError:
            delayed_exit(f'Error: permission denied writing: {log_path}', 1)
        except OSError as e:
            delayed_exit(f'Error writing {log_path}: {e}', 1)

    delayed_exit(f'Temperature control loop finished! Final temperature:\n{current_temp}', 0)


def main():
    print('Hi! This is ElchiSet!')
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Example CLI application", fromfile_prefix_chars='+')

    parser.add_argument('config_path', type=str, help='Path to configuration file')
    parser.add_argument('-s', '--setpoint', type=float, help='Heater set point')
    parser.add_argument('-p', '--prog_path', type=str, help='Setpoint program path')
    parser.add_argument('-l', '--log_path', type=str, help='Log file path')

    args = parser.parse_args()

    print('I read the following command line arguments:')
    for k, v in vars(args).items():
        print(f"{k}: {v}")

    try:
        with open(args.config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        delayed_exit(f'Error: Config file not found: {args.config_path}', 1)
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {args.config_path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {args.config_path}: {e}', 1)

    if not isinstance(config, dict):
        delayed_exit('Error: Configuration file did not contain a valid configuration.', 1)

    print('I read the following configuration:')
    for k, v in config.items():
        print(f"{k}: {v}")

    required = {'type_heater', 'port_heater', 'type_sensor', 'port_sensor', 'delta_temp', 'delta_time', 'time_res'}
    missing = required - config.keys()
    if missing:
        delayed_exit(f'Missing entries in config file: {missing}!', 1)

    match (args.setpoint is not None, args.prog_path is not None):
        case (True, True):
            delayed_exit('Invalid arguments encountered: Both setpoint and a program file specified!', 1)
        case (False, False):
            delayed_exit('Invalid arguments encountered: Neither setpoint nor program specified!', 1)
        case (True, False):
            print('Working in single setpoint mode!')
            temperature_control_loop(args.setpoint, config, args.log_path)
        case (False, True):
            print('Working in setpoint program mode!')
            setpoint = get_setpoint_from_prog(args.prog_path)
            temperature_control_loop(setpoint, config, args.log_path)


if __name__ == '__main__':
    main()
