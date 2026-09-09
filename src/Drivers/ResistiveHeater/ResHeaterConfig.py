from dataclasses import dataclass


@dataclass
class PIDConfig:
    p: float = 750
    i: float = 12
    d: float = 0


@dataclass
class ControlConfig:
    rate: float = 15


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
