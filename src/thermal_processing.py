import board
import busio
import adafruit_mlx90640
import numpy as np
import cv2


def capture_thermal_image(thermal_save_path):
    """
    Connects to the MLX90640 thermal sensor, captures a single frame,
    converts it to a false-color image, and saves it to thermal_save_path.

    Returns a tuple: (True, "Success message") or (False, "Error message")

    NOTE: Does NOT capture an RGB image - that is handled by image_capture.py.
    The thermal toggle on the dashboard simply swaps between the two saved images.
    """
    i2c = None
    try:
        # Initialize I2C and sensor INSIDE the function so startup never touches hardware
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

        # Capture thermal frame - first read clears the buffer, second is the real data
        frame = np.zeros((24 * 32,))
        mlx.getFrame(frame)  # Buffer clear
        mlx.getFrame(frame)  # Real capture

        # Reshape flat 768-element array into the 24x32 sensor grid
        data_array = np.reshape(frame, (24, 32))

        # Normalize temperature range to 0-255 for image encoding
        temp_min = np.min(data_array)
        temp_max = np.max(data_array)
        norm_data = (data_array - temp_min) / (temp_max - temp_min + 0.001)
        img_8bit = np.uint8(norm_data * 255)

        # Apply INFERNO colormap (dark=cool, bright=hot)
        thermal_img = cv2.applyColorMap(img_8bit, cv2.COLORMAP_INFERNO)

        # Scale up from 32x24 to 640x480 using nearest-neighbor (keeps pixel blocks sharp)
        thermal_display = cv2.resize(thermal_img, (640, 480), interpolation=cv2.INTER_NEAREST)

        # Save the result
        cv2.imwrite(str(thermal_save_path), thermal_display)

        import os
        if not os.path.exists(str(thermal_save_path)):
            return False, "Thermal image failed to save to disk."

        return True, "Thermal capture successful."

    except ValueError:
        # MLX90640 occasionally drops a frame over I2C - safe to retry
        return False, "Thermal sensor dropped a frame - please try again."

    except Exception as e:
        return False, f"Thermal capture error: {str(e)}"

    finally:
        # Always release the I2C bus, even if something went wrong
        if i2c is not None:
            try:
                i2c.deinit()
            except Exception:
                pass