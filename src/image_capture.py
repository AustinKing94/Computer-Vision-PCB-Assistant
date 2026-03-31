import subprocess
import os
import board
import busio
import adafruit_mlx90640
import numpy as np

# Initialize I2C and Sensor
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

def capture_raw_images(rgb_save_path):
    """
    Connects to the cameras, grabs a frame, and saves them to a dictionary to be passed to the processing script
    Returns a tuple: Boolean (True or False), Dictionary of data, or Error String
    """
    # CAPTURE RGB IMAGE
    command = [
        "/usr/bin/rpicam-still", 
        "-o", str(rgb_save_path), 
        "-t", "1000", 
        "--width", "3280", 
        "--height", "2464",
        "--nopreview"
    ]
        
    result = subprocess.run(command, capture_output=True, text=True) 
        
    if result.returncode != 0 or not os.path.exists(rgb_save_path):
        return False, f"RGB Camera command failed: {result.stderr}"

    # CAPTURE THERMAL ARRAY
    thermal_array = np.zeros((24*32,))
        
    try:
        mlx.getFrame(thermal_array)
    except ValueError:
        # The I2C bus occasionally drops a frame
        return False, "Thermal camera dropped a frame. Try again."

    # PACKAGE DATA FOR PROCESSING SCRIPT
    sensor_data = {
        "rgb_path": rgb_save_path, # Path to the file
        "thermal_array": thermal_array # 1D numpy array of sensor readings
    }

    return True, sensor_data