from configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class PIDConfig:
    p: float = 750
    i: float = 12
    d: float = 0


@dataclass
class ControlConfig:
    rate: float = 15
    power_rate: float = 100


@dataclass
class HeaterConfig:
    r_cold: float = 0.5
    max_voltage: float = 10
    max_current: float = 10
    min_output: float = 10


@dataclass
class MaterialConfig:
    """Default material configuration for resistive heater with platinum rhodium coil"""
    offset: float = 0.2
    slope: float = 0.0003


@dataclass
class ResistiveHeaterConfig:
    pid: PIDConfig
    control: ControlConfig
    heater: HeaterConfig
    material: MaterialConfig

    @classmethod
    def from_parser(cls, parser: ConfigParser, section: str) -> "ResistiveHeaterConfig":
        return cls(
            pid=PIDConfig(p=parser.getfloat(section, "P", fallback=750), i=parser.getfloat(section, "I", fallback=12),
                          d=parser.getfloat(section, "D", fallback=0)),
            control=ControlConfig(rate=parser.getfloat(section, "Rate", fallback=15),
                                  power_rate=parser.getfloat(section, "Power_Rate", fallback=100)),
            heater=HeaterConfig(r_cold=parser.getfloat(section, "R_cold", fallback=0.5),
                                max_voltage=parser.getfloat(section, "U_max", fallback=10),
                                max_current=parser.getfloat(section, "I_max", fallback=10),
                                min_output=parser.getfloat(section, "P_min", fallback=10)),
            material=MaterialConfig(offset=parser.getfloat(section, "Offset", fallback=0.2),
                                    slope=parser.getfloat(section, "Slope", fallback=0.0003)))

    def to_config_parser(self, parser: ConfigParser, section: str) -> None:
        parser[section] = {"P":      str(self.pid.p), "I": str(self.pid.i), "D": str(self.pid.d),
                           "Rate":   str(self.control.rate), "Power_Rate": str(self.control.power_rate),
                           "R_cold": str(self.heater.r_cold), "U_max": str(self.heater.max_voltage),
                           "I_max":  str(self.heater.max_current), "P_min": str(self.heater.min_output),
                           "Offset": str(self.material.offset), "Slope": str(self.material.slope)}
