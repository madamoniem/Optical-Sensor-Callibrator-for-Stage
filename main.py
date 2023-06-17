import serial
import time
import threading

class ArduinoReader:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate)
        time.sleep(2)  # allow some time for connection to be established
        self.total_X = 0
        self.total_Y = 0
        self.is_running = True

        # start the thread
        self.thread = threading.Thread(target=self._read_from_port)
        self.thread.start()

    def _read_from_port(self):
        try:
            while self.is_running:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8').strip()
                    parts = line.split(',')
                    if len(parts) == 2:
                        # Parse and assign the values correctly
                        x_part, y_part = parts
                        if ':' in x_part and ':' in y_part:
                            _, x_val = x_part.split(':')
                            _, y_val = y_part.split(':')

                            self.total_X = int(x_val.strip())
                            self.total_Y = int(y_val.strip())
        finally:
            self.ser.close()

    def distanceSinceInit(self):
        return self.total_X, self.total_Y

    def reset(self):
        self.ser.write(b'R')  # send reset signal to Arduino
        self.total_X = 0
        self.total_Y = 0

    def stop(self):
        self.is_running = False
        self.thread.join()
