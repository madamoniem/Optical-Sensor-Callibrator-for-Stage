import time
from main import ArduinoReader


arduino = ArduinoReader('COM3', 9600)


try:
        while True:
                time.sleep(1)
                total_X, total_Y = arduino.distanceSinceInit()
                print("Total X: ", total_X, "Total Y: ", total_Y)
                

except KeyboardInterrupt:
    arduino.reset()


