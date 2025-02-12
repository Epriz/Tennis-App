import cv2
import streamlit as st
from PIL import Image
import numpy as np
import time

# Set up Streamlit page
st.set_page_config(layout="wide")
st.title("Tennis Analysis App")

# Columns layout
col1, col2 = st.columns(2)

# Left column for GoPro feed
with col1:
    st.write("### Swing Visualization")

    # Checkbox to start/stop the GoPro feed
    start_feed = st.checkbox("Start/Stop GoPro Feed")

    # Placeholder for displaying the GoPro feed
    gopro_placeholder = st.empty()

    # If the checkbox is checked
    if start_feed:
        # Open GoPro camera feed
        cap = cv2.VideoCapture(1)  # Ensure this is the correct index for the GoPro

        if not cap.isOpened():
            st.error("Failed to access GoPro. Ensure it is connected and in webcam mode.")
        else:
            while start_feed:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read frame from GoPro.")
                    break

                # Convert frame to RGB (OpenCV uses BGR by default)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Update the frame in Streamlit
                gopro_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

                # Delay to allow Streamlit to update the UI
                time.sleep(0.03)  # Adjust this value if needed for smoother performance

                # Stop the loop if the checkbox is unchecked
                start_feed = st.session_state["Start/Stop GoPro Feed"]

            cap.release()

'''
with col2:



# Right column (Shot Analysis and Summary)
    st.write("### Shot Analysis and Summary")
    if shot_type in file_paths:
        file_path = file_paths[shot_type]

        # Read updated dataset
        angle, shot_acceleration = read_csv_data(file_path)

        # Perform calculations
        acceleration, indices = calculate_acceleration(shot_acceleration)

        # Reformat for impact points
        acceleration = np.round(acceleration, 2)
        acceleration_at_impact = np.array(acceleration[indices])
        shot_angle = np.round(calculate_shot_angle(angle, indices), 2)

        # Display latest shot data
        st.write(f"**Shot Angle:** {shot_angle[-1]}°")
        st.write(f"**Shot Acceleration:** {acceleration_at_impact[-1]} m/s²")

        
        # Display last 5 shots results
        st.write("### Last 5 Shots")
        last_shots = get_last_shots(shot_angle, shot_type)
        if len(last_shots) > 5:
            last_shots = last_shots[-5:]
        for result in last_shots:
            color = "green" if result == "Good" else "red"
            st.markdown(f"<span style='color: {color}; font-size: 20px;'>{result}</span>", unsafe_allow_html=True)
    else:
        st.write("No dataset available for the selected shot type.")
'''

#  python -m streamlit run Homepage.py