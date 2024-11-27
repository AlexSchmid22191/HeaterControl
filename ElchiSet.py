import argparse
import datetime
import time

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

    parser.add_argument('-s', '--setpoint', type=str, help='')

    parser.add_argument('--port_heater', type=str, help='')
    parser.add_argument('--port_sensor', type=str, help='')
    parser.add_argument('--type_heater', type=str, help='')
    parser.add_argument('--type_sensor', type=str, help='')
    parser.add_argument('--delta_time', type=str, help='')
    parser.add_argument('--delta_temp', type=str, help='')
    parser.add_argument('--time_res', type=str, help='')

    # Parse the arguments
    args = parser.parse_args()

    # Connect devices
    controller = controller_types[args.type_heater](portname=args.port_heater, slaveadress=1)
    sensor = sensor_types[args.type_sensor](port=args.port_sensor)

    # Set the temeprature
    controller.set_target_setpoint(float(args.setpoint))

    # Count down from delta_time to zero
    # Measure temeperature every time_res seconds
    # Reset if the temperature deviates by more than delta_temp
    time_left = float(args.delta_time)
    last_measurement_time = time.time()
    last_measurement_temp = sensor.get_sensor_value()
    while time_left > 0:
        if time.time() - last_measurement_time < float(args.time_res):
            # Less than time_res seconds have passed since the last measurement, do nothing
            continue

        last_measurement_time = time.time()
        current_temp = sensor.get_sensor_value()
        print(f'Current temeprature: {current_temp}')
        if abs(current_temp - last_measurement_temp) > float(args.delta_temp):
            # Temeprature varies by more than delta_temp
            # Reset the coundown and set the current temperature as reference for constancy
            time_left = float(args.delta_time)
            last_measurement_temp = sensor.get_sensor_value()
        else:
            # Temperature stays within delta_temp, decrease remaining time by time_res
            time_left -= float(args.time_res)
        print(f'Time left: {time_left}')

    with open('Logfile.txt', 'a') as logfile:
        now = datetime.datetime.now(datetime.UTC)
        logfile.write(f'{int(now.timestamp())}, {now.strftime('%Y-%m-%d %H:%M:%S')} UTC, {last_measurement_temp} C\n')


if __name__ == '__main__':
    main()
