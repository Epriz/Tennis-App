import requests
import time
import threading
import queue

data_queue = queue.Queue()  # Queue to store processed data 

def noraxon_stream_collect(stream_config, max_retries=3, timeout=60):
    """
    Collects data from the Noraxon MR3 stream indefinitely until stopped by the user.

    Args:
        stream_config (dict): Stream configuration object.
        max_retries (int): Maximum number of retries for failed requests.
        timeout (int): Timeout duration for each request in seconds.

    Returns:
        tuple: Two lists containing angles and accelerations.
    """
    if "server_url" not in stream_config or "channelinfo" not in stream_config:
        raise ValueError("Invalid stream configuration provided.")
    
    server_url = stream_config["server_url"]
    collect_url = f"{server_url}/samples"
    angle_data = []  # To hold angle values
    acceleration_data = []  # To hold acceleration values
    retry_count = 0

    # Create a session for persistent connections
    session = requests.Session()

    print(f"Starting data collection from {collect_url}")
    print(f"Stream Configuration: Name:{stream_config['channelinfo'][0]['name']}, Type:{stream_config['channelinfo'][0]['type']}")

    def collect_data():
        nonlocal angle_data, acceleration_data
        try:

            acceleration_data = []  # List to store acceleration (Z component)
            angle_data = []         # List to store angle (all components)
            while True:
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
                            #print("Skipping empty data entry.")
                            continue  # Skip processing if no channels in data

                        # Debugging: Print the raw data structure
                        #print("Received Data:", json.dumps(data, indent=2))
                        acceleration_channel = channels[0:1]
                        angle_channel = channels[1:]
                        #print(angle_channel[0]['samples'])
                        #print(type(angle_channel))
                        

                    except ValueError as e:
                        print(f"Error parsing JSON response: {e}")
                        continue  # Skip this iteration if response is not valid JSON

                    # Process the data
                    for channel in angle_channel:
                        #print("Processing angle channel:", channel)  # Debugging the channel structure
                        if 'samples' in channel:
                            angle_data.extend(channel['samples'])  # Append all angle samples
                        else:
                            print("No 'samples' key found in angle channel.")

                    for channel in acceleration_channel:
                        #print("Processing acceleration channel:", channel)  # Debugging the channel structure
                        if 'samples' in channel:
                            acceleration_data.extend(channel['samples'][2::3])  # Append all acceleration samples
                        else:
                            print("No 'samples' key found in acceleration channel.")

                    data_queue.put((angle_data, acceleration_data))  # Put initial data into the queue
                    
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

    # Allow the user to stop collection at any time by pressing Enter
    #input("Press Enter to stop data collection...")  # Wait for user input to stop
    while collection_thread.is_alive():
        time.sleep(1)  # Wait for the collection thread to finish

    #print(f"Data collection completed. Total samples collected: {len(angle_data)}")
    return angle_data, acceleration_data
