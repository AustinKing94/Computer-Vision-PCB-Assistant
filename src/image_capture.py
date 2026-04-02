import subprocess
import os
import board
import busio
import adafruit_mlx90640
import numpy as np

def capture_raw_images(rgb_save_path):
    """
    Connects to the cameras, grabs a frame, and saves them to a dictionary to be passed to the processing script
    Returns a tuple: Boolean (True or False), Dictionary of data, or Error String
    """
    try:
        # 1. Initialize hardware ONLY when called
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
        
        # 2. CAPTURE RGB IMAGE
        command = [
            "/usr/bin/rpicam-still", 
            "-o", str(rgb_save_path), 
            "-t", "500", # Reduced timeout to speed up the demo
            "--width", "3280", 
            "--height", "2464",
            "--nopreview"
        ]
        subprocess.run(command, capture_output=True, text=True) 

        # 3. CAPTURE THERMAL ARRAY
        thermal_array = np.zeros((24*32,))
        
        # Give the sensor a moment to stabilize
        mlx.getFrame(thermal_array) # First read to clear buffer
        mlx.getFrame(thermal_array) # Actual data capture

        sensor_data = {
            "rgb_path": rgb_save_path,
            "thermal_array": thermal_array
        }
        
        # 4. Clean up the I2C bus for the next call
        i2c.deinit() 
        return True, sensor_data

    except Exception as e:
        return False, f"Hardware Error: {str(e)}"