from noraxon_stream_init_calibration import noraxon_stream_init
from noraxon_stream_collect_calibration import noraxon_stream_collect
from initial_calibration import Offset_x, Offset_y, Offset_z
import numpy as np
import time

'''This script performs a calibration, to determine
   the difference in orientation as for x, y and z 
   between the hand sensor and the racket sensor.
   Differently to the previous calibration, this one
   needs to be performed every time, as grip and hand
   size may vary between players, therefore affect the
   offset angles.'''

# Initialize the Noraxon MR3 stream and collect calibration data
def initialize_and_calibrate():
    """Initialize the Noraxon MR3 stream and collect calibration data."""
    try:
        print("Initializing Noraxon MR3 stream for calibration...")
        #stream_config = noraxon_stream_init("192.168.8.124", 5939)
        print("Stream initialized successfully.")

        print("Calibrating...press Enter to stop.")
        #angle_data_x, angle_data_y, angle_data_z = noraxon_stream_collect(stream_config)


        print("Calibration complete.")
        return #angle_data_x, angle_data_y, angle_data_z

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

# Calculate offsets for calibration
def calculate_offsets(angle_x_data, angle_y_data, angle_z_data, Offset_x, Offset_y, Offset_z):
    """Calculate the total offsets based on the calibration data."""
    mean_x = np.mean(angle_x_data)
    mean_y = np.mean(angle_y_data)
    mean_z = np.mean(angle_z_data)

    Offset_x_rac = round(mean_x, 2)
    Offset_y_rac = round(mean_y, 2)
    Offset_z_rac = round(mean_z, 2)

    Offset_x_total = Offset_x + Offset_x_rac
    Offset_y_total = Offset_y + Offset_y_rac
    Offset_z_total = Offset_z + Offset_z_rac

    return Offset_x_total, Offset_y_total, Offset_z_total

Offset_x_total = None
Offset_y_total = None
Offset_z_total = None

def main():
    try:
        # Phase 1: Data Collection
        angle_data_x, angle_data_y, angle_data_z = initialize_and_calibrate()

        if angle_data_x is None or angle_data_y is None or angle_data_z is None:
            print("Data collection failed.")
            return

        # Phase 2: Ensure Data Collection Completeness
        print("Checking if data collection is complete...")
        while True:
            previous_length = len(angle_data_x)
            # Pause briefly to allow for data growth if still collecting
            time.sleep(1)

            # Check if data has stopped growing
            if len(angle_data_x) == previous_length:
                print("Data collection finalized.")
                print(len(angle_data_x))
                break
            else:
                print("Still collecting data...")

        return calculate_offsets(angle_data_x, angle_data_y, angle_data_z, Offset_x, Offset_y, Offset_z)
    
    except Exception as e:
        print(f"Error: {e}")
    
    

if __name__ == "__main__":
    main()
