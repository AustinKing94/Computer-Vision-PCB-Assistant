import subprocess
import os

def capture_raw_images(rgb_save_path, thermal_save_path=None):
    """
    Connects to the cameras, grabs a frame, and saves them directly to the provided paths.
    """
    try:
        # Using rpicam-still for Raspberry Pi OS Bookworm
        # -o : output file path
        # -t 1000 : wait 1 second (1000ms) for auto-exposure/white balance to settle
        # --width 1920 --height 1080 : set your desired resolution
        # --nopreview : don't try to open a display window on the Pi
        
        command = [
            "/usr/bin/rpicam-still", 
            "-o", str(rgb_save_path), 
            "-t", "1000", 
            "--width", "1920", 
            "--height", "1080",
            "--nopreview"
        ]
        
        # Run the command and wait for it to finish
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Check if the command was successful and the file was actually created
        if result.returncode == 0 and os.path.exists(rgb_save_path):
            return True, "Capture successful"
        else:
            # Print the exact error to the terminal for debugging
            print(f"CAMERA ERROR LOG:\nReturn Code: {result.returncode}\nError: {result.stderr}")
            return False, f"Camera command failed: {result.stderr}"
            
    except Exception as e:
        # Let's force it to print the system error if it crashes here
        print(f"SYSTEM CRASH LOG: {str(e)}") 
        return False, f"System error: {str(e)}"
