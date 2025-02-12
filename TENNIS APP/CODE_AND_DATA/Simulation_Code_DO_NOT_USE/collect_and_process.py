import numpy as np
import pandas as pd
from config import hand, shot_type
import threading
import time

# Global buffers
angle_data_buffer = []
acceleration_data_buffer = []
results_buffer = []  # Stores shot evaluation results
Offset_y_total = 4.5
# Constants for processing
ACCELERATION_THRESHOLD = 2000
ANGLE_BUFFER_SIZE = 100
ACCELERATION_BUFFER_SIZE = 100
sampling_interval = 0.005  # Time interval between samples (in seconds)
peak_count = 10  # Number of peaks in the acceleration data
angle_frequency = 2 * np.pi / 2  # Frequency of the sinusoidal angle oscillation (for 2 seconds period)

# Global variables to store data
last_acceleration_at_poi = None  # Acceleration value at the point of impact
last_angle_at_poi = None  # Angle value at the point of impact
last_shot_evaluation = []  # Last shot evaluation results

# Initialize time and sample counter for simulation
total_time = 0  # Start at time 0
sample_counter = 0

# Function to simulate live acceleration data with multiple peaks and plateaus
def generate_acceleration_value(t, peak_count=10, total_time=20, plateau_duration=0.2):
    acceleration_value = 0
    peak_width = 0.10  # Control the width of the peak
    peak_height = np.random.uniform(0.5, 2)  # Random height for variability
    time_between_peaks = total_time / (peak_count + 1)  # Space the peaks evenly over the total time

    for i in range(peak_count):
        peak_center = (i + 1) * time_between_peaks  # Center of each peak
        plateau_start = peak_center + peak_width  # Start of plateau after the peak
        plateau_end = plateau_start + plateau_duration  # End of plateau

        # If the current time 't' falls within a peak region, generate a peak
        if t >= peak_center - peak_width and t <= peak_center + peak_width:
            # Gaussian peak generation
            acceleration_value += peak_height * np.exp(-((t - peak_center) ** 2) / (2 * peak_width ** 2))
        elif t >= plateau_start and t <= plateau_end:
            # Plateau region, low or no acceleration
            acceleration_value += np.random.uniform(0, 0.1)  # Low acceleration during plateau

    return acceleration_value

# Function to simulate live angle data as a sinusoidal wave
def generate_angle_value(t, frequency=angle_frequency):
    # Use a sine wave to model the angle of the racket
    angle_value = 15 * np.sin(frequency * t)  # Amplitude of 15 degrees, adjust frequency for speed of oscillation
    return angle_value

# Replace the Noraxon stream collection with simulated data
def initialize_and_collect_simulated():
    """Simulate data collection."""
    global total_time, sample_counter
    
    # Simulate a batch of new data points for acceleration and angle
    acceleration_value = generate_acceleration_value(total_time, peak_count=peak_count)
    angle_value = generate_angle_value(total_time)
    
    # Append the new values to the buffers
    time_data = [total_time]
    acceleration_data = [acceleration_value]
    angle_data = [angle_value]
    
    # Update the global time and counter for simulation
    total_time += sampling_interval
    sample_counter += 1
    
    # Return the simulated data
    return angle_data, acceleration_data

# Offset correction for angle data
def offset_correction(angle):
    """Perform offset correction of the angle data."""
    angle_data = angle - Offset_y_total
    return angle_data

# Update and process acceleration buffer
def live_calculate_acceleration(new_acceleration_data):
    """Update acceleration buffer and detect impacts."""
    global acceleration_data_buffer, last_acceleration_at_poi
    
    # Append new data to the buffer
    acceleration_data_buffer.extend(new_acceleration_data)
    if len(acceleration_data_buffer) > ACCELERATION_BUFFER_SIZE:
        acceleration_data_buffer = acceleration_data_buffer[-ACCELERATION_BUFFER_SIZE:]

    # Detect impact indices above the threshold
    indices_above_threshold = [
        i for i, val in enumerate(acceleration_data_buffer) if val > ACCELERATION_THRESHOLD
    ]
    
    # Identify impact points
    impact_indices = []
    for i in range(1, len(indices_above_threshold)):
        if indices_above_threshold[i] != indices_above_threshold[i - 1] + 1:
            impact_indices.append(indices_above_threshold[i - 1])
    if indices_above_threshold and indices_above_threshold[-1] != indices_above_threshold[-2] + 1:
        impact_indices.append(indices_above_threshold[-1])

    # Store the acceleration at the point of impact (POI) if there are any impact points
    if impact_indices:
        last_acceleration_at_poi = acceleration_data_buffer[impact_indices[-1]]

    return impact_indices

# Update and process angle buffer
def live_calculate_shot_angle(new_angle_data, impact_indices):
    """Update angle buffer and calculate shot angles."""
    global angle_data_buffer, last_angle_at_poi

    # Append new data to the buffer
    angle_data_buffer.extend(new_angle_data)
    if len(angle_data_buffer) > ANGLE_BUFFER_SIZE:
        angle_data_buffer = angle_data_buffer[-ANGLE_BUFFER_SIZE:]

    # Extract angles at impact points
    corrected_angles = offset_correction(angle_data_buffer)
    shot_angles = [corrected_angles[i] for i in impact_indices if i < len(corrected_angles)]

    # Store the angle at the point of impact (POI) if there are any impact points
    if shot_angles:
        last_angle_at_poi = shot_angles[-1]

    return shot_angles

# Evaluate the last few shots
def live_get_last_shots(shot_angles):
    """Evaluate the last 5 shots."""
    global results_buffer

    # Evaluate shots based on type and hand
    shot_evaluation = []
    for angle in shot_angles:
        if shot_type == "Topspin":
            if hand == "Left" and 12 < angle < 30:
                shot_evaluation.append("Good")
            elif hand == "Right" and -30 < angle < -12:
                shot_evaluation.append("Good")
            else:
                shot_evaluation.append("Bad")
        elif shot_type == "Flat":
            if hand == "Left" and 75 < angle < 85:
                shot_evaluation.append("Good")
            elif hand == "Right" and -85 < angle < -75:
                shot_evaluation.append("Good")
            else:
                shot_evaluation.append("Bad")
        elif shot_type == "Backspin":
            if hand == "Left" and 30 < angle < 50:
                shot_evaluation.append("Good")
            elif hand == "Right" and -50 < angle < -30:
                shot_evaluation.append("Good")
            else:
                shot_evaluation.append("Bad")
    
    # Store the last 5 results
    results_buffer.extend(shot_evaluation)
    if len(results_buffer) > 5:
        results_buffer = results_buffer[-5:]

    return results_buffer

# Getter functions to access shot data
def get_last_acceleration_at_poi():
    """Get the last acceleration value at the point of impact."""
    return last_acceleration_at_poi

def get_last_angle_at_poi():
    """Get the last angle value at the point of impact."""
    return last_angle_at_poi

def get_last_shot_evaluation():
    """Get the last shot evaluation results."""
    return results_buffer

stop_flag = threading.Event()  # Initialize the threading event

# Main live processing loop
def main():
    """Simulate the live processing loop."""
    while not stop_flag.is_set():  # Continue processing until stop flag is set
        # Collect data from the simulated stream
        angle_data, acceleration_data = initialize_and_collect_simulated()
        
        if angle_data and acceleration_data:
            # Process live data
            impact_indices = live_calculate_acceleration(acceleration_data)
            if impact_indices:  # Only process if impacts are detected
                shot_angles = live_calculate_shot_angle(angle_data, impact_indices)
                last_shots = live_get_last_shots(shot_angles)
                print(f"Last Shots: {last_shots}")

        time.sleep(0.1)  # Delay between data collection (adjust as needed)

    print("Live processing stopped.")  # Print when processing stops

# Start live processing in a separate thread
def start_live_processing():
    """Start live processing in a separate thread."""
    global stop_flag
    stop_flag.clear()  # Reset the stop flag
    processing_thread = threading.Thread(target=main, daemon=True)
    processing_thread.start()

# Stop live processing
def stop_live_processing():
    """Stop live processing."""
    global stop_flag
    stop_flag.set()  # Signal the loop to stop

# Start the live loop
if __name__ == "__main__":
    start_live_processing()
    time.sleep(5)  # Run the loop for 5 seconds (simulating)
    stop_live_processing()  #
