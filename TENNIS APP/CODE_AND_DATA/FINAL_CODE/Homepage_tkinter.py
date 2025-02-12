import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import config
import collections
from collect_and_calibrate import main as calibration_main  # Import calibration function
from collect_and_process import start_live_processing, stop_live_processing, data_queue_eval
import queue

# Global variables
calibration_complete = False
measurement_running = False
cap = None  # For GoPro feed
go_pro_feed_running = False  # Initialize GoPro feed state

# Store the last 5 evaluation results
evaluation_history = collections.deque(maxlen=5)  # Store the last 5 evaluation results

# Dropdown menu options
handedness_options = ["Right", "Left"]
shot_type_options = ["Topspin", "Flat", "Backspin"]

# Function to toggle GoPro feed
def toggle_feed():
    global cap, go_pro_feed_running

    if go_pro_feed_running:
        go_pro_feed_running = False
        if cap:
            cap.release()
            cap = None
        go_pro_label.configure(image="")
        start_stop_button.config(text="Start GoPro Feed")
    else:
        cap = cv2.VideoCapture(0)  # Ensure this is the correct index for the GoPro
        if not cap or not cap.isOpened():
            messagebox.showerror("Error", "Failed to access GoPro. Ensure it is connected and in webcam mode.")
            return
        go_pro_feed_running = True
        start_stop_button.config(text="Stop GoPro Feed")
        update_feed()

# Function to update the GoPro feed
def update_feed():
    global cap, go_pro_label, go_pro_feed_running

    if not go_pro_feed_running:
        return

    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Failed to read frame from GoPro.")
        return

    frame = cv2.resize(frame, (480, 360))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    go_pro_label.imgtk = imgtk
    go_pro_label.configure(image=imgtk)
    go_pro_label.after(30, update_feed)

# Function to run calibration
def run_calibration():
    global calibration_complete
    global Offset_x_total, Offset_y_total, Offset_z_total

    def calibration_task():
        calibration_button.config(state=tk.DISABLED)

        # Update status label
        def update_status_label(status):
            calibration_status_label.config(text=status)

        root.after(0, update_status_label, "Connecting...")

        # Start calibration process
        Offset_x_total, Offset_y_total, Offset_z_total = calibration_main()

        # Simulate calibration completion for UI update
        root.after(0, update_status_label, "Calibrating...")
        for i in range(1, 101):
            root.after(50 * i, progress_bar.config, {"value": i})

        root.after(5000, update_status_label, "Calibration Status: Complete")
        root.after(5000, calibration_button.config, {"state": tk.NORMAL})
        # Simulate calculated offsets (replace with actual values from calibration_main if available)
        calculated_offsets = {"Offset X": np.round(Offset_x_total, 1), "Offset Y": np.round(Offset_y_total, 1), "Offset Z": np.round(Offset_z_total, 1)}

        # Create a frame to display the offsets
        offsets_frame = ttk.LabelFrame(calibration_frame, text="Calculated Offsets")
        offsets_frame.pack(pady=10)

        for key, value in calculated_offsets.items():
            offset_label = ttk.Label(offsets_frame, text=f"{key}: {value}")
            offset_label.pack()
    calibration_complete = True

    threading.Thread(target=calibration_task).start()

# Function to run measurement
def run_measurement():
    global measurement_running

    if not calibration_complete:
        messagebox.showwarning("Warning", "Calibration not performed. Measurement results might be inaccurate.")

    if not measurement_running:
        measurement_running = True
        measurement_button.config(state=tk.DISABLED)
        
        # Pass selections to the external measurement script
        shot_type = selected_shot_type.get()
        handedness = selected_handedness.get()
    threading.Thread(target=start_live_processing).start()

# Function to update the GUI with the latest data
def update_gui_from_queue():
    """Retrieve data from the queue and update the GUI."""
    if not data_queue_eval.empty():
        angle_data, acceleration_data, results = data_queue_eval.get()
        
        # Call the update_evaluation function with the latest data
        update_evaluation(angle_data, acceleration_data, results)
        
    # Call this function again after 100 milliseconds to keep checking for new data
    root.after(100, update_gui_from_queue)
    return angle_data, acceleration_data, results



# Stop measurement function
def stop_measurement():
    global measurement_running
    if measurement_running:
        measurement_running = False
        measurement_button.config(state=tk.NORMAL)
        stop_live_processing()

#def update_gui_from_queue():
#    """Retrieve data from the queue and update the GUI."""
#    while not data_queue_eval.empty():
#        shot_angles, acceleration_data, results = data_queue_eval.get()
#        update_gui_evaluation(shot_angles, acceleration_data, results)
#    root.after(100, update_gui_from_queue)
#    return shot_angles, acceleration_data, results


# Function to update shot angle, acceleration, and evaluation
def update_evaluation(angle_data, acceleration_data, results):
    # Update the angle and acceleration labels with the latest values
    angle_label.config(text=f"Angle: {angle_data[-1]:.2f}°")  # Show the last value in angle_data
    acceleration_label.config(text=f"Acceleration: {acceleration_data[-1]:.2f} m/s²")  # Show the last value in acceleration_data
    evaluation_label.config(text=f"Evaluation: {results[-1]}", foreground="green" if results[-1] == "Good" else "red")

    # Update the evaluation display for the last 5 results
    for i, eval_result in enumerate(results):
        # Display only the evaluation results (no angle/acceleration in this section)
        eval_label = ttk.Label(evaluation_frame, text=f"Evaluation: {eval_result}", 
                               foreground="green" if eval_result == "Good" else "red")
        eval_label.grid(row=i, column=2, sticky="w", padx=10, pady=5)
    



# Initialize the root window
root = tk.Tk()
root.title("Tennis Analysis App")
root.geometry("1000x600")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Dropdown menu variables
selected_handedness = tk.StringVar(value="Right")
selected_shot_type = tk.StringVar(value="Topspin")

# Function to update the shot type label dynamically
def update_shot_type_label(*args):
    shot_type_label.config(text=f"Shot Type: {selected_shot_type.get()}")
    config.shot_type = selected_shot_type.get()

# Function to pass handedness to config.py (handedness doesn't affect the UI)
def update_handedness():
    config.update_handedness(selected_handedness.get())

# Attach trace to the selected_shot_type variable
selected_shot_type.trace_add("write", update_shot_type_label)

# Load logo
try:
    logo_image = Image.open("/Users/tommaso/Università /MCI Bachelor MGST/Kurse/5. Semester/Project/TENNIS APP 2/CODE_AND_DATA/FINAL_CODE/Tennis Shot Analyzer.jpeg")  # Replace with the path to your logo
    logo_image = logo_image.resize((200, 150), Image.Resampling.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo_image)
except Exception as e:
    logo_tk = None
    print(f"Error loading logo: {e}")

# Measurement Tab
measurement_frame = ttk.Frame(notebook)
notebook.add(measurement_frame, text="Measurement")

feed_and_analysis_frame = ttk.Frame(measurement_frame)
feed_and_analysis_frame.pack(fill=tk.BOTH, expand=True)

# GoPro feed
go_pro_label = ttk.Label(feed_and_analysis_frame)
go_pro_label.pack(side=tk.LEFT, padx=10, pady=10)

# Shot analysis frame
analysis_frame = ttk.LabelFrame(feed_and_analysis_frame, text="Shot Analysis")
analysis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

shot_type_label = ttk.Label(analysis_frame, text="Shot Type: Select")
shot_type_label.pack()

if logo_tk:
    measurement_logo_label = ttk.Label(analysis_frame, image=logo_tk)
    measurement_logo_label.pack(side=tk.BOTTOM, pady=10)

# Combobox for Shot Type
label_shot = ttk.Label(feed_and_analysis_frame, text="Select Shot Type:")
label_shot.pack(side=tk.BOTTOM, padx=5)
shot_type_combobox = ttk.Combobox(feed_and_analysis_frame, textvariable=selected_shot_type, values=shot_type_options, state="readonly")
shot_type_combobox.pack(side=tk.BOTTOM, pady=5)
shot_type_combobox.set("Select Shot Type")

# Combobox for Hand Selection
label_hand = ttk.Label(feed_and_analysis_frame, text="Select Hand:")
label_hand.pack(side=tk.BOTTOM, padx=5)
hand_combobox = ttk.Combobox(feed_and_analysis_frame, textvariable=selected_handedness, values=handedness_options, state="readonly")
hand_combobox.pack(side=tk.BOTTOM, pady=5)
hand_combobox.set("Select Hand")

# Buttons for GoPro and Measurement
buttons_frame = ttk.Frame(measurement_frame)
buttons_frame.pack(fill=tk.X, pady=20)

start_stop_button = ttk.Button(buttons_frame, text="Start GoPro Feed", command=toggle_feed)
start_stop_button.pack(side=tk.LEFT, padx=10)

measurement_button = ttk.Button(buttons_frame, text="Start Measurement", command=run_measurement)
measurement_button.pack(side=tk.LEFT, padx=10)

stop_button = ttk.Button(buttons_frame, text="Stop Measurement", command=stop_measurement)
stop_button.pack(side=tk.LEFT, padx=10)

# Create labels for angle, acceleration, and evaluation
angle_label = ttk.Label(analysis_frame, text="Angle: N/A")
angle_label.pack(side=tk.TOP, padx=10, pady=5)

acceleration_label = ttk.Label(analysis_frame, text="Acceleration: N/A")
acceleration_label.pack(side=tk.TOP, padx=10, pady=5)

evaluation_label = ttk.Label(analysis_frame, text="Evaluation: N/A")
evaluation_label.pack(side=tk.TOP, padx=10, pady=5)

# Calibration Tab
calibration_frame = ttk.Frame(notebook)
notebook.add(calibration_frame, text="Calibration")

calibration_button = ttk.Button(calibration_frame, text="Start Calibration", command=run_calibration)
calibration_button.pack(pady=20)

calibration_status_label = ttk.Label(calibration_frame, text="Calibration Status: Not started")
calibration_status_label.pack()

progress_bar = ttk.Progressbar(calibration_frame, length=200, mode="determinate")
progress_bar.pack()

# Add a frame to display the evaluation results
evaluation_frame = ttk.LabelFrame(feed_and_analysis_frame, text="Shot Evaluation", padding=(10, 5))
evaluation_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)


if logo_tk:
    calibration_logo_label = ttk.Label(calibration_frame, image=logo_tk)
    calibration_logo_label.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
