import threading
import minimalmodbus
from Drivers.AbstractSensorController import AbstractController, AbstractSensor
import time


dev = minimalmodbus.Instrument('COM20', slaveaddress=1)
dev.serial.baudrate = 9600

while True:
    try:
        print(dev.read_register(0x0026))
    except:
        pass

