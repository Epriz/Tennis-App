import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from initial_calibration import Offset_x, Offset_y, Offset_z
from noraxon_stream_collect_calibration import angle_x_data, angle_y_data, angle_z_data

# Calculate the mean for each axis (X, Y, Z)
mean_x = np.mean(angle_x_data)
mean_y = np.mean(angle_y_data)
mean_z = np.mean(angle_z_data)

# Round the means to 2 decimal places
Offset_x_rac = round(mean_x, 2)
Offset_y_rac = round(mean_y, 2)
Offset_z_rac = round(mean_z, 2)

# Calculate the total offsets by summing the imported offset and the mean
Offset_x_total = Offset_x + Offset_x_rac
Offset_y_total = Offset_y + Offset_y_rac
Offset_z_total = Offset_z + Offset_z_rac

# Print the results
print("The total offset in the angle between hand sensor and racket sensor is: ")
print(f"X: {Offset_x_total}, Y: {Offset_y_total}, Z: {Offset_z_total}")