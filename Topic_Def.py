# Automatically generated by TopicTreeSpecPrinter(**kwargs).
# The kwargs were:
# - fileObj: TextIOWrapper
# - footer: '# End of topic tree definition. Note that application may l...'
# - indentStep: 4
# - treeDoc: None
# - width: 70


class engine:
    """
    UNDOCUMENTED: created as parent without specification
    """

    class answer:
        """
        UNDOCUMENTED: created as parent without specification
        """

        class process_variable:
            """
            UNDOCUMENTED: created without spec
            """
            
            def msgDataSpec(pv):
                """
                - temp: UNDOCUMENTED
                """

        class working_output:
            """
            UNDOCUMENTED: created without spec
            """
            
            def msgDataSpec(output):
                """
                - output: UNDOCUMENTED
                """

        class working_setpoint:
            """
            UNDOCUMENTED: created without spec
            """
            
            def msgDataSpec(setpoint):
                """
                - setpoint: UNDOCUMENTED
                """

        class sensor_value:
            """
            UNDOCUMENTED: created without spec
            """
            
            def msgDataSpec(value):
                """
                - temp: UNDOCUMENTED
                """

    class status:
        """

        """
        def msgDataSpec(text):
            """
            - text: UNDOCUMENTED
            """

class gui:
    """
    UNDOCUMENTED: created as parent without specification
    """

    class con:
        """
        UNDOCUMENTED: created as parent without specification
        """

        class connect_heater:
            """
            UNDOCUMENTED: created without spec
            """
            
            def msgDataSpec(heater_type, heater_port):
                """
                - heater_port: UNDOCUMENTED
                - heater_type: UNDOCUMENTED
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

    class set:
        """
        UNDOCUMENTED: created as parent without specification
        """

        class automatic_mode:
            """
            UNDOCUMENTED: created without spec
            """

        class manual_mode:
            """
            UNDOCUMENTED: created without spec
            """

        class manual_power:
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

        class target_setpoint:
            """
            UNDOCUMENTED: created without spec
            """
            
            def msgDataSpec(temp):
                """
                - temp: UNDOCUMENTED
                """


# End of topic tree definition. Note that application may load
# more than one definitions provider.
