import time
import threading
import requests

def noraxon_stream_collect(stream_config, max_retries=3, timeout=60, collect_duration=5):
    """
    Collects data from the Noraxon MR3 stream for a limited duration (default 5 seconds).

    Args:
        stream_config (dict): Stream configuration object.
        max_retries (int): Maximum number of retries for failed requests.
        timeout (int): Timeout duration for each request in seconds.
        collect_duration (int): Duration for collecting data in seconds.

    Returns:
        tuple: Three lists containing angles in x, y, and z components.
    """
    if "server_url" not in stream_config or "channelinfo" not in stream_config:
        raise ValueError("Invalid stream configuration provided.")
    
    server_url = stream_config["server_url"]
    collect_url = f"{server_url}/samples"
    angle_x_data = []  # To hold angle values in the x component
    angle_y_data = []  # To hold angle values in the y component
    angle_z_data = []  # To hold angle values in the z component
    retry_count = 0

    # Create a session for persistent connections
    session = requests.Session()

    print(f"Starting data collection from {collect_url}")
    print(f"Stream Configuration: Name:{stream_config['channelinfo'][0]['name']}, Type:{stream_config['channelinfo'][0]['type']}")

    def collect_data():
        nonlocal angle_x_data, angle_y_data, angle_z_data
        start_time = time.time()  # Record the start time for the 5-second limit
        try:
            while time.time() - start_time < collect_duration:  # Collect for the specified duration
                try:
                    # Send a request to collect data
                    response = session.get(collect_url, timeout=timeout)
                    response.raise_for_status()  # Raise exception for HTTP errors

                    # Try parsing the response JSON
                    try:
                        data = response.json()  # Parse JSON response
                        
                        channels = data['channels']
                        # Skip if the channels list is empty (first data entry)
                        if not channels:
                            print("Skipping empty data entry.")
                            continue  # Skip processing if no channels in data

                        # Extracting angle data from the channels
                        # Assuming channels 0:1, 1:2, and 2:3 correspond to x, y, and z components respectively
                        angle_x_channel = channels[0:1]  # Channel 0:1 for x angles
                        angle_y_channel = channels[1:2]  # Channel 1:2 for y angles
                        angle_z_channel = channels[2:3]  # Channel 2:3 for z angles

                    except ValueError as e:
                        print(f"Error parsing JSON response: {e}")
                        continue  # Skip this iteration if response is not valid JSON

                    # Process the angle data for each channel
                    # Process x angle
                    for channel in angle_x_channel:
                        if 'samples' in channel:
                            angle_x_data.extend(channel['samples'])
                        else:
                            print("No 'samples' key found in x angle channel.")

                    # Process y angle
                    for channel in angle_y_channel:
                        if 'samples' in channel:
                            angle_y_data.extend(channel['samples'])
                        else:
                            print("No 'samples' key found in y angle channel.")

                    # Process z angle
                    for channel in angle_z_channel:
                        if 'samples' in channel:
                            angle_z_data.extend(channel['samples'])
                        else:
                            print("No 'samples' key found in z angle channel.")

                    retry_count = 0  # Reset retries on successful request
                    time.sleep(0.1)  # Simulate a short delay between collections
                except requests.exceptions.ReadTimeout:
                    retry_count += 1
                    print(f"Read timeout occurred. Retrying ({retry_count}/{max_retries})...")
                    if retry_count > max_retries:
                        print("Max retries reached. Stopping data collection.")
                        break
                    time.sleep(5)  # Backoff before retrying
                except requests.exceptions.RequestException as e:
                    print(f"HTTP Error during collection: {e}")
                    break  # Stop on persistent HTTP errors
        except KeyboardInterrupt:
            print("Data collection interrupted by user.")
        except Exception as e:
            print(f"Unexpected error during data collection: {e}")
            raise ConnectionError(f"Could not collect data from {collect_url}.") from e
        finally:
            session.close()  # Ensure the session is properly closed

    # Start collecting data in a separate thread
    collection_thread = threading.Thread(target=collect_data)
    collection_thread.daemon = True  # Allow the thread to exit when the program ends
    collection_thread.start()

    # Wait until the collection thread finishes or the 5 seconds are up
    collection_thread.join()

    print(f"Data collection completed. Total samples collected: {len(angle_x_data)}")
    return angle_x_data, angle_y_data, angle_z_data