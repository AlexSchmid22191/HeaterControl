import time


class SoftwarePID:
    def __init__(self, pb, ti, td):
        self.pb = pb
        self.ti = ti
        self.td = td

        self.last_process_variable = 0
        self.output_sum = 0

        self.interval = 0.25  # seconds
        self.last_update = time.time()

    def calculate_output(self, process_variable, setpoint):
        kp, ki, kd = self._transform_pid_params(self.pb, self.ti, self.td)

        if now := time.time() - self.last_update > self.interval:
            error = setpoint - process_variable
            d_pv = process_variable - self.last_process_variable

            self.output_sum += ki * error
            self.output_sum = self._constrain(self.output_sum)

            output = error * kp + self.output_sum# + d_pv * kd
            output = self._constrain(output, _min=12)

            print(f'P Term: {error * kp}')
            print(f'I Term: {self.output_sum}')
            print(time.time())


            self.last_process_variable = process_variable
            self.last_update = now

            return output

    @staticmethod
    def _constrain(value, _min=0, _max=100):
        return max(min(_max, value), _min)

    def _transform_pid_params(self, pb, ti, td):
        kp = 100 / pb
        ki = kp / ti * self.interval
        kd = kp * td / self.interval

        return kp, ki, kd
