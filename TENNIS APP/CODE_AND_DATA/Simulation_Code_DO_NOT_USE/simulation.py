import numpy as np
import matplotlib.pyplot as plt

# Parameters
sampling_interval = 0.005  # Time interval between samples (in seconds)
num_samples_max = 50000  # Max number of samples before the user stops (can be adjusted)
peak_count = 5  # Number of peaks in the acceleration data
angle_frequency = 2 * np.pi / 2  # Frequency of the sinusoidal angle oscillation (for 2 seconds period)

# Initialize empty lists to store the time, acceleration, and angle data
time_data = []
acceleration_data = []
angle_data = []

# Function to simulate live acceleration data with multiple peaks and plateaus
def generate_acceleration_value(t, peak_count=15, total_time=20, plateau_duration=0.1):
    acceleration_value = 0
    peak_width = 0.05  # Control the width of the peak
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

# Start collecting data
print("Starting live data collection. Type 'stop' to finish.")

total_time = 0  # Start at time 0
sample_counter = 0

# Create a way to stop the collection using user input
import threading
import time

# Variable to control when to stop the loop
stop_collection = False

# Function to listen for user input to stop the collection
def listen_for_stop():
    global stop_collection
    while not stop_collection:
        user_input = input("Type 'stop' to finish data collection: ")
        if user_input.lower() == 'stop':
            stop_collection = True

# Start listening for the stop input in a separate thread
input_thread = threading.Thread(target=listen_for_stop)
input_thread.start()

# Collect data while stop_collection is False
while not stop_collection and sample_counter < num_samples_max:
    # Simulate the new data point (acceleration and angle)
    acceleration_value = generate_acceleration_value(total_time, peak_count=peak_count)
    angle_value = generate_angle_value(total_time)
    
    # Append data to the lists
    time_data.append(total_time)
    acceleration_data.append(acceleration_value)
    angle_data.append(angle_value)
    
    # Update time and counter
    total_time += sampling_interval
    sample_counter += 1
    
    # Wait for a small time before the next data entry (mimicking the real-time collection)
    time.sleep(sampling_interval)

# Stop the input thread after data collection is finished
input_thread.join()

# Plotting the data after collection
plt.figure(figsize=(12, 6))

# Acceleration plot
plt.subplot(2, 1, 1)
plt.plot(time_data, acceleration_data, label='Acceleration')
plt.title('Simulated Live Acceleration Data with Peaks and Plateaus')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.grid(True)
plt.legend()

# Angle plot
plt.subplot(2, 1, 2)
plt.plot(time_data, angle_data, label='Angle', color='orange')
plt.title('Simulated Live Angle Data (Sinusoidal)')
plt.xlabel('Time (s)')
plt.ylabel('Angle (degrees)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
