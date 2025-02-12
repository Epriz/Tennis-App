import requests

def noraxon_stream_init(server_ip="172.20.10.10", port=5939):
    server_url = f"http://{server_ip}:{port}"
    headers_url = f"{server_url}/headers"
    disable_url = f"{server_url}/disable/"
    enable_url = f"{server_url}/enable/"
    
    print(f"Connecting to server: {server_url}")
    
    try:
        response = requests.get(headers_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to MR3 stream at {server_url}. Ensure HTTP streaming is enabled and a measurement is running.") from e
    
    if "headers" not in data or not data["headers"]:
        raise ValueError("No data sources found.")
    
    headers = data["headers"]
    selected_indices = [21, 11]  # Hardcoded indices for sensor angle and sensor acceleration
    
    try:
        requests.get(f"{disable_url}all", timeout=10)
        print("Disabled all channels.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not disable channels at {server_url}. Ensure HTTP streaming is enabled and a measurement is running.") from e
    
    stream_config = {"server_url": server_url, "channelinfo": []}
    for index in selected_indices:
        header = headers[index]
        channel_info = {
            "name": header["name"],
            "type": header["type"].replace("real.", "").replace("vector3.accel", "acceleration").replace("vector3.rot", "quaternion").replace("vector3.pos", "position").replace("switch", "on/off"),
            "full_type": header["type"],
            "sample_rate": header["samplerate"],
            "units": header["units"],
            "index": header["index"]
        }
        stream_config["channelinfo"].append(channel_info)
        
        try:
            requests.get(f"{enable_url}{header['index']}", timeout=10)
            print(f"Enabled channel: Name:{channel_info['name']}, Type:{channel_info['type']}")
        except requests.exceptions.RequestException as e:
            print(f"Error enabling channel {header['name']}: {e}")
            raise ConnectionError(f"Could not enable channel {header['name']} at {server_url}.") from e
    
    print(f"Stream configuration complete.")
    return stream_config
