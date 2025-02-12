import subprocess

def start_noraxon_data_stream():
    # Run the noraxon_stream_data script as a separate process
    subprocess.Popen(['python', 'noraxon_stream_data.py'])

start_noraxon_data_stream()

import numpy as np
import pandas as pd
#from hand_racket_calibration import Offset_x_total
from noraxon_stream_data import angle_data, acceleration_data


shot_acceleration = acceleration_data
shot_angle = angle_data

def get_shot_types():
    """Return a list of shot types."""
    return ["Topspin", "Flat", "Backspin"]

def hand_selection():
    """Return a list of shot types."""
    return ["Left", "Right"]

def get_last_shots(angle, shot_type, hand):
    """Return the results of the last 5 shots."""
    shot_evaluation = []
    for i in range(len(angle)):
        if shot_type == "Topspin":
            if hand == "Left":
                if 12 < angle[i] < 30:  # Adjusted range for left hand
                    shot_evaluation.append("Good")
                else:
                    shot_evaluation.append("Bad")
            elif hand == "Right":
                if -30 < angle[i] < -12:  # Original range for right hand
                    shot_evaluation.append("Good")
                else:
                    shot_evaluation.append("Bad")
        elif shot_type == "Flat":
            if hand == "Left":
                if 75 < angle[i] < 85:  # Adjusted range for left hand
                    shot_evaluation.append("Good")
                else:
                    shot_evaluation.append("Bad")
            elif hand == "Right":
                if -85 < angle[i] < -75:  # Original range for right hand
                    shot_evaluation.append("Good")
                else:
                    shot_evaluation.append("Bad")
        elif shot_type == "Backspin":
            if hand == "Left":
                if 30 < angle[i] < 50:  # Adjusted range for left hand
                    shot_evaluation.append("Good")
                else:
                    shot_evaluation.append("Bad")
            elif hand == "Right":
                if -50 < angle[i] < -30:  # Original range for right hand
                    shot_evaluation.append("Good")
                else:
                    shot_evaluation.append("Bad")

    if len(shot_evaluation) > 5:
        shot_evaluation.pop(0)

    return shot_evaluation

def calculate_shot_angle(angle, indices):

    # Convert shot_angle to NumPy array if it's a pandas Series
    shot_angle_array = angle.to_numpy() if isinstance(angle, pd.Series) else shot_angle
    
    # Extract angle values at the given indices
    shot_angle = shot_angle_array[indices]
    
    return shot_angle

def calculate_acceleration(acceleration):
    """Calculate and return acceleration for point of impact."""
    # calculate the indices of the acceleration
    indices_above_2000 = np.where(acceleration > 2000)[0]

    # Initialize list to store the indices of the peaks
    indices = []
    
    # Iterate over the indices where the acceleration exceeds 2000
    for i in range(1, len(indices_above_2000)):
        # Check if the previous index is not consecutive (i.e., a new peak starts), if index list is empty, return error message
        try:
            if indices_above_2000[i] != indices_above_2000[i-1] + 1:
                indices.append(indices_above_2000[i-1])
        except:
            return "No peaks found, no impact detected"
    
    # Append the last index if it's part of a peak
    if indices_above_2000[-1] != indices_above_2000[-2] + 1:
        indices.append(indices_above_2000[-1])
    
    return acceleration, indices

# call the functions
shot_type = get_shot_types()
acceleration, indices = calculate_acceleration(shot_acceleration)
shot_angle = calculate_shot_angle(shot_angle, indices)
shot_evaluation = get_last_shots(shot_angle, get_shot_types(), hand_selection())