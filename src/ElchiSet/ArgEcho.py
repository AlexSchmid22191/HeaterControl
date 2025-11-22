import argparse
from ElchiSetBase import delayed_exit


def main():
    print('Hi! This is ArgEcho!')

    parser = argparse.ArgumentParser(
        description='ArgEcho is a helper script to echo all received command line arguments!',
        fromfile_prefix_chars='+')

    parser.add_argument('args', nargs='*', help='Arbitrary positional args')

    args = parser.parse_args()
    print('I read the following command line arguments:')
    print(args)

    delayed_exit('Done!')


if __name__ == '__main__':
    main()
