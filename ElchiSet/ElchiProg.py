# A command line program to sequentiall set heater temepratures written in a program file
# After each temperature set, wait until a separate sensor shows that the temperature is constant
# Arguments: [prog_path], [log_path], [config_path]
# Any of those can be omitted, in which case default paths are used

import argparse
import datetime
import ElchiSetBase as Esb
from pathlib import Path
from platformdirs import user_data_dir


def read_lines(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        Esb.delayed_exit(f'Error: File not found: {path}', 1)
    except PermissionError:
        Esb.delayed_exit(f'Error: Permission denied reading: {path}', 1)
    except OSError as e:
        Esb.delayed_exit(f'Error reading {path}: {e}', 1)


def write_lines(path: str, lines):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except PermissionError:
        Esb.delayed_exit(f'Error: permission denied writing: {path}', 1)
    except OSError as e:
        Esb.delayed_exit(f'Error writing {path}: {e}', 1)


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
        Esb.delayed_exit('All entries in program file processed!', 0)

    raw = lines[idx].strip()
    try:
        setpoint = float(raw)
    except (ValueError, TypeError) as e:
        Esb.delayed_exit(f'Error converting setpoint {raw!r}: {e}', 1)
    else:
        lines[idx] = mark_processed(lines[idx])
        write_lines(filepath, lines)
        return setpoint


def main():
    print('Hi! This is ElchiProg!')

    parser = argparse.ArgumentParser(
        description='ElchiProg is a CLI application for setting a temeprature setpoint via a PID controller (heater)'
                    ' and monitoring via a temeprature sensor if the temperature has reached a steady state!\n'
                    'Each invocation of this program sequentially processes entries in a program file as setpoints!',
        fromfile_prefix_chars='+')

    parser.add_argument('-p', '--prog_path', type=str, help='Setpoint program file path, optional')
    parser.add_argument('-c', '--config_path', type=str, help='Configuration file path, optional')
    parser.add_argument('-l', '--log_path', type=str, help='Log file path, optional')

    args = parser.parse_args()

    print('I read the following command line arguments:')
    for k, v in vars(args).items():
        print(f"{k}: {v}")

    if args.config_path is None:
        data_dir = Path(user_data_dir('ElchiProg', 'ElchWorks', roaming=True))
        data_dir.mkdir(parents=True, exist_ok=True)
        args.config_path = data_dir / 'default_config.yaml'
        print(f'Using default config file path: {args.config_path}')

    if args.log_path is None:
        data_dir = Path(user_data_dir('ElchiProg', 'ElchWorks', roaming=True))
        data_dir.mkdir(parents=True, exist_ok=True)
        args.log_path = data_dir / f'log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        print(f'Using default log file path: {args.log_path}')

    if args.prog_path is None:
        data_dir = Path(user_data_dir('ElchiProg', 'ElchWorks', roaming=True))
        data_dir.mkdir(parents=True, exist_ok=True)
        args.prog_path = data_dir / f'default_prog.txt'
        print(f'Using default program file path: {args.prog_path}')

    config = Esb.load_config(args.config_path)
    Esb.validate_config(config)

    setpoint = get_setpoint_from_prog(args.prog_path)
    Esb.temperature_control_loop(setpoint, config, args.log_path)


if __name__ == '__main__':
    main()
