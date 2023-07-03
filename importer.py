import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial.distance import euclidean

initial_y = []
final_y = []
calibration_factors_y = []

for i in range(len(calibration_results)):
    initial_y.append(calibration_results[i]['Initial_Sensor_Y'])
    final_y.append(calibration_results[i]['Final_Sensor_Y'])
    calibration_factors_y.append(calibration_results[i]['Calibration_Factor_Y'])

initial_y = np.array(initial_y)
final_y = np.array(final_y)
calibration_factors_y = np.array(calibration_factors_y)

mean_calibration_factor_y = np.mean(calibration_factors_y)

# Create a scatter plot for start and stop positions
fig, axs = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)

# Start positions plot
scatter = axs[0].scatter(np.arange(len(initial_y)), mean_calibration_factor_y*initial_y, alpha=0.5)
axs[0].set_title("Start Positions")
axs[0].set_xlabel('Data Points')
axs[0].set_ylabel('$y$ (mm)')
axs[0].grid(True)

# Stop positions plot
scatter = axs[1].scatter(np.arange(len(final_y)), mean_calibration_factor_y*final_y, alpha=0.5)
axs[1].set_title("Stop Positions")
axs[1].set_xlabel('Data Points')
axs[1].set_ylabel('$y$ (mm)')
axs[1].grid(True)

# Display the plots
plt.show()

# 2D scatter plot of Sensor Positions
plt.figure(figsize=(8,8))
plt.scatter(initial_y, final_y, alpha=0.5)
plt.title('2D Scatter plot of Sensor Positions')
plt.xlabel('Initial Y')
plt.ylabel('Final Y')
plt.grid(True)
plt.show()
