from noraxon_stream_init import noraxon_stream_init
from noraxon_stream_collect import noraxon_stream_collect
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
        print(f"Collecting data...press Enter to stop.")
        angle_data, acceleration_data = noraxon_stream_collect(stream_config)

        # Optionally print the results for debugging
        print(f"Acceleration Data: {acceleration_data}")
        print(f"Angle Data: {angle_data}")

        print(f"Data collection complete.")

        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
