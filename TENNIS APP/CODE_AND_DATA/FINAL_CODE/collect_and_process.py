import time
import numpy as np
import threading
from noraxon_stream_init import noraxon_stream_init
from noraxon_stream_collect import noraxon_stream_collect, data_queue
from collect_and_calibrate import main as initialize_and_calibrate
from config import hand, shot_type
from tkinter import messagebox
import queue

# Global buffers for storing results
angle_data_buffer = []
acceleration_data_buffer = []
results_buffer = []  # Stores shot evaluation results

data_queue_eval = queue.Queue()  # Queue to store processed data

# Constants
ACCELERATION_THRESHOLD = 1000
ANGLE_BUFFER_SIZE = 100
ACCELERATION_BUFFER_SIZE = 100
MAX_RESULTS = 5

# Threading setup
stop_flag = threading.Event()

#Offset_x_total, Offset_y_total, Offset_z_total = initialize_and_calibrate()

# Initialize Noraxon stream
def initialize_stream():
    """Initialize Noraxon MR3 stream."""
    try:
        print("Initializing Noraxon MR3 stream...")
        return noraxon_stream_init("192.168.8.124", 5939)
    except Exception as e:
        print(f"Error initializing stream: {e}")
        return None

def collect_data(stream_config):
    """Continuously collect data from the Noraxon stream and process it."""
    threading.Thread(target=noraxon_stream_collect, args=(stream_config,), daemon=True).start()
    while not stop_flag.is_set():
        try:
            angle_data, acceleration_data = data_queue.get()  # Get data from the queue
            if angle_data and acceleration_data:
                process_and_evaluate(angle_data, acceleration_data)
        except queue.Empty:
            print("Warning: No data in queue.")
        except Exception as e:
            print(f"Data collection error: {e}")

        time.sleep(0.05)  # Adjust sampling interval
    

# Offset correction
def offset_correction(angle_data):
    """Perform offset correction of the angle data."""
    return np.array(angle_data) - Offset_y_total

# Detect impact events
def detect_impacts_and_process_angles(acceleration_data, angle_data):
    """Detect impacts and extract corresponding shot angles while ensuring synchronization."""

    if len(acceleration_data) >= 4 * len(angle_data):  # Ensure we can downsample
        # Downsample acceleration to match angle data length
        downsampled_accel = acceleration_data[::4]  # Take every 4th sample
    else:
        downsampled_accel = acceleration_data  # Use as-is if already matched
    impact_indices = [i for i, val in enumerate(downsampled_accel) if val > ACCELERATION_THRESHOLD]

    if not impact_indices:
        return [], [], []

    angle_data = offset_correction(angle_data)

    # Ensure indices are within bounds to prevent errors
    valid_indices = [i for i in impact_indices if i < len(angle_data)]

    angle_data = [angle_data[i] for i in valid_indices]
    #convert from float64 to regular float
    angle_data = [float(i) for i in angle_data]
    downsampled_accel = [acceleration_data[i] for i in valid_indices]

    return downsampled_accel, angle_data, valid_indices



# Evaluate shots
def evaluate_shots(angle_data, hand, shot_type):
    """Determine shot quality based on type and hand."""
    global results_buffer
    shot_evaluation = []

        # Skip processing if angle_data is empty
    if not angle_data:
        print("No valid shot performed yet. Skipping evaluation.")

    for i in range(len(angle_data)):
        if shot_type == "Topspin":
            shot_evaluation.append("Good" if (hand == "Left" and 12 < angle_data[i] < 30) or 
                                            (hand == "Right" and -30 < angle_data[i] < -12) else "Bad")
        elif shot_type == "Flat":
            shot_evaluation.append("Good" if (hand == "Left" and 75 < angle_data[i] < 100) or 
                                            (hand == "Right" and -100 < angle_data[i] < -75) else "Bad")
        elif shot_type == "Backspin":
            shot_evaluation.append("Good" if (hand == "Left" and 30 < angle_data[i] < 50) or 
                                            (hand == "Right" and -50 < angle_data[i] < -30) else "Bad")

    # Store the last MAX_RESULTS evaluations
    results_buffer = (results_buffer + shot_evaluation)[-MAX_RESULTS:]
    
    return results_buffer

# Function to process and evaluate the data
def process_and_evaluate(angle_data, acceleration_data):
    """Process incoming angle and acceleration data."""
    acceleration_data, angle_data, impact_indices = detect_impacts_and_process_angles(acceleration_data, angle_data)
    
    print(f"Impact indices detected: {impact_indices}")  # Debug print

    if impact_indices:


        results = evaluate_shots(angle_data, hand, shot_type)

        print(f"Last Shots: {results}")

        # ✅ Send only the new results to the queue
        data_queue_eval.put((angle_data, acceleration_data, results))

        # ✅ Clear processed data to prevent re-processing the same impact
        angle_data.clear()
        acceleration_data.clear()


#def update_gui_evaluation(angle, acceleration, evaluation):
#    """This function will be called to update the GUI with shot evaluation data."""
#    # Here, we need to call the update_evaluation function directly from the GUI script
#    from Homepage_tkinter import update_evaluation
#    # Pass data to the GUI update function
#    update_evaluation(angle, acceleration, evaluation)

# Live processing loop
def start_live_processing():
    """Starts data collection and real-time processing in separate threads."""
    global stop_flag
    stop_flag.clear()
    stream_config = initialize_stream()
    
    if not stream_config:
        print("Failed to initialize stream.")
        return
    
    # Start data collection thread
    threading.Thread(target=collect_data, args=(stream_config,), daemon=True).start()
 

# Stop live processing
def stop_live_processing():
    """Stops all live processing."""
    stop_flag.set()

