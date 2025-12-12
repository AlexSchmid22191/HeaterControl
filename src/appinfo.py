APP_NAME = 'ElchiTools'
APP_VERSION_NUMERIC = (3, 2, 1, 0)
APP_VERSION = f'{APP_VERSION_NUMERIC[0]}.{APP_VERSION_NUMERIC[1]}'

if APP_VERSION_NUMERIC[2] != 0:
    APP_VERSION += f'.{APP_VERSION_NUMERIC[2]}'
    if APP_VERSION_NUMERIC[3] != 0:
        APP_VERSION += f'.{APP_VERSION_NUMERIC[3]}'

APP_DESCRIPTION = 'A desktop application for interfacing with PID heater and voltage controllers and sensors.'
APP_AUTHOR = 'Alex Schmid'
APP_COPYRIGHT = '© 2025 Alex Schmid'
APP_COMPANY = 'TU Wien'
APP_SOURCE = 'https://github.com/AlexSchmid22191/HeaterControl'
APP_CONTACT = 'alex.schmid91@gmail.com'
APP_LICENSE = 'GPL 3.0'
