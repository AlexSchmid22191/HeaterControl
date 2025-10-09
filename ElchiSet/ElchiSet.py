import argparse
import datetime
import ElchiSetBase as Esb
from pathlib import Path
from platformdirs import user_data_dir


def main():
    print('Hi! This is ElchiSet!')

    parser = argparse.ArgumentParser(
        description='ElchiSet is a CLI application for setting a temeprature setpoint via a PID controller (heater) and'
                    ' monitoring via a temeprature sensor if the temperature has reached a steady state!',
        fromfile_prefix_chars='+')

    parser.add_argument('setpoint', type=float, help='Temeprature setpoint')
    parser.add_argument('-c', '--config_path', type=str, help='Configuration file path, optional')
    parser.add_argument('-l', '--log_path', type=str, help='Log file path, optional')

    args = parser.parse_args()

    print('I read the following command line arguments:')
    for k, v in vars(args).items():
        print(f"{k}: {v}")

    if args.config_path is None:
        data_dir = Path(user_data_dir('ElchiSet', 'ElchWorks', roaming=True))
        data_dir.mkdir(parents=True, exist_ok=True)
        args.config_path = data_dir / 'default_config.yaml'
        print(f'Using default config file path: {args.config_path}')

    if args.log_path is None:
        data_dir = Path(user_data_dir('ElchiSet', 'ElchWorks', roaming=True))
        data_dir.mkdir(parents=True, exist_ok=True)
        args.log_path = data_dir / f'log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        print(f'Using default log file path: {args.log_path}')

    config = Esb.load_config(args.config_path)
    Esb.validate_config(config)
    Esb.temperature_control_loop(args.setpoint, config, args.log_path)


if __name__ == '__main__':
    main()
