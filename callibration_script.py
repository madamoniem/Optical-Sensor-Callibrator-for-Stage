# WORK IN PROGRESS, I DON'T KNOW WHAT I'M DOING

# initialize stage instance and zero axes
stage = motion_stage()
stage.home_axes()

# initialize ArduinoReader
arduino = ArduinoReader('COM3', 9600)  # replace with your port 

# Calibrate the sensor
# Set the calibration distance, in mm. The greater the distance, the more accurate the calibration.
calibration_distance = 100.0  # in mm

# Record initial sensor readings
initial_sensor_x, initial_sensor_y = arduino.distanceSinceInit()

# Move the stage
stage.move_x_absolute(calibration_distance)
stage.move_y_absolute(calibration_distance)

# Record sensor readings after moving
final_sensor_x, final_sensor_y = arduino.distanceSinceInit()

# Calculate the sensor's reported movement
sensor_movement_x = final_sensor_x - initial_sensor_x
sensor_movement_y = final_sensor_y - initial_sensor_y

# Calculate calibration factors
calibration_factor_x = calibration_distance / sensor_movement_x
calibration_factor_y = calibration_distance / sensor_movement_y

# Print calibration factors
print(f"Calibration factor for X: {calibration_factor_x}")
print(f"Calibration factor for Y: {calibration_factor_y}")

# cleanup
arduino.stop()
