from noraxon_stream_init import noraxon_stream_init
from noraxon_stream_collect_calibration import noraxon_stream_collect
import csv

def main():
    """
    Main function to initialize the Noraxon MR3 stream and collect data.
    """
    try:
        # Initialize stream configuration
        print("Initializing Noraxon MR3 stream...")
        stream_config = noraxon_stream_init("192.168.8.124", 5939)
        print("Stream initialized successfully.")


        # Collect data
        print(f"Calibrating...press Enter to stop.")
        angle_data_x, angle_data_y, angle_data_z = noraxon_stream_collect(stream_config)

        print(f"Calibration complete.")

        print(angle_data_x)
        print(angle_data_y)
        print(angle_data_z)

        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
