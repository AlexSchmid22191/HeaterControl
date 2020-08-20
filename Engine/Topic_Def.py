# Automatically generated by TopicTreeSpecPrinter(**kwargs).
# The kwargs were:
# - fileObj: TextIOWrapper
# - footer: '# End of topic tree definition. Note that application may l...'
# - indentStep: 4
# - treeDoc: None
# - width: 70


class engine:
    """
    Superclass for all messages emitted by the engine
    """
    class spam:
        """
        UNDOCUMENTED: created without spec
        """
        def msgDataSpec(status_values):
            """
            - status_values: float
            """

    class broadcast:
        """
        Class for all briadcasts from the engine (typically done at initialization)
        """
        class devices:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(ports, devices):
                """
                - ports: list
                - devices: dict
                """
    class answer:
        """
        Class for all answers to requests from the GUI
        """
        class status:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(status_values):
                """
                - status_values: dict
                """
        class control_parameters:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(control_parameters):
                """
                - control_parameters: dict
                """
        class pid:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(pid_parameters):
                """
                - pid_parameters: dict
                """

class gui:
    """
    Superclass for all messages emitted by the GUI
    """
    class con:
        """
        UNDOCUMENTED: created as parent without specification
        """
        class connect_controller:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(controller_type, controller_port):
                """
                - controller_type: UNDOCUMENTED
                - controller_port: UNDOCUMENTED
                """
        class connect_sensor:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(sensor_type, sensor_port):
                """
                - sensor_port: UNDOCUMENTED
                - sensor_type: UNDOCUMENTED
                """
        class disconnect_controller:
            """
            UNDOCUMENTED: created without spec
            """

        class disconnect_sensor:
            """
            UNDOCUMENTED: created without spec
            """

    class set:
        """
        UNDOCUMENTED: Class for all set command from the GUI (i.e. unidirectional commands wirthout expected repsonse)
        """
        class control_mode:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(mode):
                """
                - mode: UNDOCUMENTED
                """
        class power:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(power):
                """
                - power: UNDOCUMENTED
                """
        class rate:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(rate):
                """
                - rate: UNDOCUMENTED
                """
        class setpoint:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(setpoint):
                """
                - setpoint: UNDOCUMENTED
                """
        class pid_parameter:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(parameter, value):
                """
                - parameter: string
                - value: float or string
                """

    class plot:
        """
        A class for everthing related to the logging module
        """
        class start:
            """
            UNDOCUMENTED: created without spec
            """
        class stop:
            """
            UNDOCUMENTED: created without spec
            """
        class clear:
            """
            UNDOCUMENTED: created without spec
            """
        class export:
            """
            UNDOCUMENTED: created without spec
            """
            def msgDataSpec(filepath):
                """
                - filepath: UNDOCUMENTED
                """

    class request:
        """
        Class for all requests from the gui
        """
        class status:
            """
            """
        class devices:
            """
            """

# End of topic tree definition. Note that application may load
# more than one definitions provider.
