import subprocess
import os
import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import cv2
from pathlib import Path

# Initialize I2C and Sensor
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

def capture_raw_images(rgb_save_path, thermal_save_path):
    """
    Connects to the cameras, grabs a frame, and saves them directly to the provided paths.
    """
    try:
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
            print(f"CAMERA ERROR LOG:\nReturn Code: {result.returncode}\nError: {result.stderr}")
            return False, f"RGB Camera command failed: {result.stderr}"

        # CAPTURE THERMAL IMAGE
        frame = np.zeros((24*32,))
        
        try:
            mlx.getFrame(frame)
        except ValueError:
            # The I2C bus occasionally drops a frame
            return False, "Thermal camera dropped a frame. Try again."

        # Reshape the 1D array to the 24x32 sensor grid
        data_array = np.reshape(frame, (24, 32))
        
        # Normalize temperatures to a 0-255 scale
        temp_min = np.min(data_array)
        temp_max = np.max(data_array)
        norm_data = (data_array - temp_min) / (temp_max - temp_min + 0.001)
        img_8bit = np.uint8(norm_data * 255)
        
        # Apply a thermal color map
        thermal_img = cv2.applyColorMap(img_8bit, cv2.COLORMAP_INFERNO)
        
        # Scale up strictly using raw pixel blocks (no smoothing) to 640x480
        thermal_display = cv2.resize(thermal_img, (640, 480), interpolation=cv2.INTER_NEAREST)
        
        # Save the thermal image
        cv2.imwrite(str(thermal_save_path), thermal_display)

        if os.path.exists(rgb_save_path) and os.path.exists(thermal_save_path):
            return True, "Both captures successful"
        else:
            return False, "One or both files failed to save."
            
    except Exception as e: 
        return False, f"System error: {str(e)}"