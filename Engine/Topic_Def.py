class engine:
    """
    Superclass for all messages emitted by the engine
    """
    class answer:
        """
        Class for all answers to requests from the GUI
        """
        class ports:
            """
            """
            def msgDataSpec(ports):
                """
                - ports: dict
                """
        class devices:
            """
            """
            def msgDataSpec(devices):
                """
                - devices: dict
                """
        class status:
            """
            """
            def msgDataSpec(status_values):
                """
                - status_values: dict
                """
        class control_parameters:
            """
            """
            def msgDataSpec(control_parameters):
                """
                - control_parameters: dict
                """
        class pid_parameters:
            """
            """
            def msgDataSpec(pid_parameters):
                """
                - pid_parameters: dict
                """

    class status:
        """
        """
        def msgDataSpec(text):
            """
            - ports: text
            """

class gui:
    """
    Superclass for all messages emitted by the GUI
    """
    class con:
        """
        Everthing relatesd to serial connections
        """
        class connect_controller:
            """
            """
            def msgDataSpec(controller_type, controller_port):
                """
                - controller_type: string
                - controller_port: string
                """
        class connect_sensor:
            """
            """
            def msgDataSpec(sensor_type, sensor_port):
                """
                - sensor_port: string
                - sensor_type: string
                """
        class disconnect_controller:
            """
            """
        class disconnect_sensor:
            """
            """

    class set:
        """
        UNDOCUMENTED: Class for all set command from the GUI (i.e. unidirectional commands without expected repsonse)
        """
        class control_mode:
            """
            """
            def msgDataSpec(mode):
                """
                - mode: string
                """
        class power:
            """
            """
            def msgDataSpec(power):
                """
                - power: float
                """
        class rate:
            """
            """
            def msgDataSpec(rate):
                """
                - rate: flaot
                """
        class setpoint:
            """
            """
            def msgDataSpec(setpoint):
                """
                - setpoint: flaot
                """
        class pid_parameters:
            """
            """
            def msgDataSpec(parameter, value):
                """
                - parameter: string
                - value: float or string
                """
        class units:
            """
            """
            def msgDataSpec(unit):
                """
                - unit: string
                """

    class plot:
        """
        A class for everthing related to plotting/logging
        """
        class start:
            """
            """
        class stop:
            """
            """
        class clear:
            """
            """
        class export:
            """
            """
            def msgDataSpec(filepath):
                """
                - filepath: string
                """

    class request:
        """
        Class for all requests from the gui
        """
        class status:
            """
            """
        class ports:
            """
            """
        class control_parameters:
            """
            """
        class pid_parameters:
            """
            """
