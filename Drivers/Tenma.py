import threading

from serial import Serial


class Tenma(Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.com_lock = threading.Lock()

    def set_voltage_limit(self, voltage):
        string = f'VSET05:{voltage:.3f}'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')

    def set_current_limit(self, current):
        string = f'ISET05:{current:.3f}'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')

    def get_voltage_limit(self):
        string = f'VSET05?'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            return float(answer.decode())

    def get_current_limit(self):
        string = f'ISET05?'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            return float(answer.decode())

    def get_voltage(self):
        string = f'VOUT05?'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            return float(answer.decode())

    def get_current(self):
        string = f'IOUT05?'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            return float(answer.decode())

    def get_limit_mode(self):
        # TODO
        string = f'STATUS05?'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            return 'CV' if answer.decode()[-1] == '0' else 'CC'

    def get_resistance(self):
        string_c = f'IOUT05?'
        string_v = f'VOUT05?'
        with self.com_lock:
            self.write(string_c.encode())
            self.write(b'\x0D')
            answer_c = self.readline()
            self.write(string_v.encode())
            self.write(b'\x0D')
            answer_v = self.readline()

            voltage = float(answer_v.decode())
            current = float(answer_c.decode())
            if current < 0.1:
                return -1
            else:
                return voltage / current
