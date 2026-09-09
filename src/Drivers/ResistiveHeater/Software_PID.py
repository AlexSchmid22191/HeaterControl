import time

from src.Drivers.ResistiveHeater.ResHeaterConfig import PIDConfig


class SoftwarePID:
    def __init__(self, pid_conf: PIDConfig, loop_interval: float = 0.25):
        self.conf = pid_conf

        self.last_process_variable = 0.0
        self.output_sum = 0.0

        self.interval = loop_interval  # seconds
        self.last_update = time.time()

    def calculate_output(self, process_variable: float, setpoint: float) -> float | None:
        kp, ki, kd = self._transform_pid_params(self.conf.p, self.conf.i, self.conf.d)

        now = time.time()
        if now - self.last_update > self.interval:
            error = setpoint - process_variable
            d_pv = process_variable - self.last_process_variable

            self.output_sum += ki * error
            self.output_sum = self._constrain(self.output_sum)

            output = error * kp + self.output_sum - d_pv * kd

            output = self._constrain(output)
            self.last_process_variable = process_variable
            self.last_update = now

            return output
        else:
            return None

    @staticmethod
    def _constrain(value: float, _min: float = 0, _max: float = 100) -> float:
        return max(min(_max, value), _min)

    def _transform_pid_params(self, pb: float, ti: float, td: float) -> tuple[float, float, float]:
        kp = 100 / pb
        ki = kp / ti * self.interval
        kd = kp * td / self.interval

        return kp, ki, kd
