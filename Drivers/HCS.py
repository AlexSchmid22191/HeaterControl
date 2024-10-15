from serial import Serial
import threading


class HCS34(Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.com_lock = threading.Lock()

    def readline(self):
        return self.read_until(b'\r').rstrip(b'\r')

    def set_voltage_limit(self, voltage):
        string = f'VOLT{int(voltage*10):03d}'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'

    def set_current_limit(self, current):
        string = f'CURR{int(current*10):03d}'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', f'No or invalid response from device! Response {ack_answer}'

    def get_voltage_limit(self):
        string = f'GETS'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'
            return float(answer.decode()[:3]) / 10

    def get_current_limit(self):
        string = f'GETS'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'
            return float(answer.decode()[3:]) / 10

    def get_voltage(self):
        string = f'GETD'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'
            return float(answer.decode()[:4]) / 100

    def get_current(self):
        string = f'GETD'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'
            return float(answer.decode()[4:8]) / 100

    def get_limit_mode(self):
        string = f'GETD'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'
            return 'CV' if answer.decode()[-1] == '0' else 'CC'

    def get_resistance(self):
        string = f'GETD'
        with self.com_lock:
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            ack_answer = self.readline()
            assert ack_answer.decode() == 'OK', 'No response from device'
            voltage = float(answer.decode()[:4])
            current = float(answer.decode()[4:8])
            if current < 100:
                return -1
            else:
                return voltage / current
