import cv2

def capture_raw_images(rgb_save_path, thermal_save_path=None):
    """
    Connects to the cameras, grabs a frame, and saves them directly to the provided paths.
    """
    try:
        # Initialize the standard camera (0 is usually the default Pi/USB cam)
        cap = cv2.VideoCapture(0)
        
        # Give the sensor a fraction of a second to adjust to light levels
        # (Optional, but helps prevent dark frames)
        for _ in range(5):
            cap.read()
            
        ret, frame = cap.read()
        
        if ret:
            # Save the image directly to the path provided by app.py
            cv2.imwrite(rgb_save_path, frame)
            
            # TODO: Add your MLX90640 thermal camera capture logic here later!
            # If you capture a thermal frame, you would save it like this:
            # cv2.imwrite(thermal_save_path, thermal_frame)
            
            cap.release()
            return True, "Capture successful"
        else:
            cap.release()
            return False, "Failed to read from camera"
            
    except Exception as e:
        return False, f"Camera error: {str(e)}"