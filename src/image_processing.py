import cv2
import cv2.aruco as aruco
import numpy as np
from image_capture import capture_raw_images
from thermal_processing import thermal_processed
from analyzer import PCBAnalyzer
pcb_analyzer = PCBAnalyzer()

# Methods for modularity -----------------------------------------------------------------

# Uses sum and difference to calculate which marker is in each corner of the image
def find_marker_positions(corners, ids):
    # Get representative point (center) for each marker
    centers = []
    for marker in corners:
        points = marker.reshape((4, 2)) # Simplifies corners array returned by ArUco
        center = np.mean(points, axis=0) # Finds center of each marker
        centers.append(center) # Append to list
    
    # Find which marker is in each corner using min/max of sum or diff
    top_left_idx = min(range(len(centers)), key=lambda i: centers[i][0] + centers[i][1])
    top_right_idx = max(range(len(centers)), key=lambda i: centers[i][0] - centers[i][1])
    bottom_right_idx = max(range(len(centers)), key=lambda i: centers[i][0] + centers[i][1])
    bottom_left_idx = min(range(len(centers)), key=lambda i: centers[i][0] - centers[i][1])
    
    # Map indexes to corners to keep access to coordinates
    marker_locations = {
        "top_left": top_left_idx,
        "top_right": top_right_idx,
        "bottom_right": bottom_right_idx,
        "bottom_left": bottom_left_idx
    }

    return marker_locations 

# Uses corner cooridantes to define region of interest (inner corner of each marker)
def define_roi(corners, ids, marker_locations):
    roi_coordinates = [] # List of ROI coordinates in order top left, top right, bottom right, bottom left
    roi_coordinates.append(corners[(marker_locations["top_left"])][0][2])
    roi_coordinates.append(corners[(marker_locations["top_right"])][0][3])
    roi_coordinates.append(corners[(marker_locations["bottom_right"])][0][0])
    roi_coordinates.append(corners[(marker_locations["bottom_left"])][0][1])

    return(roi_coordinates)

# Uses coordinates to do perspective transformation on the raw image (Calls methods above)
def process_and_flatten_image(input_image_path, output_image_path):
    """
    Reads an image, detects 4 ArUco markers, extracts the ROI, 
    performs a perspective warp to flatten it, and saves the result.
    """
    # Read the image
    img = cv2.imread(str(input_image_path))
    if img is None:
        print(f"Error: Could not read image at {input_image_path}")
        return False

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Initialize ArUco detector
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    # Detect markers
    corners, ids, rejected = detector.detectMarkers(gray)

    # Ensure we found exactly 4 markers for a 4-point perspective transform
    if ids is not None and len(ids) >= 4:
        marker_locations = find_marker_positions(corners, ids)
        roi_coordinates = define_roi(corners, ids, marker_locations)
        
        # Organize the ROI points (the inner corners of the markers)
        src_pts = np.array([
            roi_coordinates[0], # Top Left
            roi_coordinates[1], # Top Right
            roi_coordinates[2], # Bottom Right
            roi_coordinates[3]  # Bottom Left
        ], dtype="float32")

        # Calculate the maximum width and height of the new flat image
        # Using Pythagorean theorem to find the longest edge
        widthA = np.sqrt(((src_pts[2][0] - src_pts[3][0]) ** 2) + ((src_pts[2][1] - src_pts[3][1]) ** 2))
        widthB = np.sqrt(((src_pts[1][0] - src_pts[0][0]) ** 2) + ((src_pts[1][1] - src_pts[0][1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((src_pts[1][0] - src_pts[2][0]) ** 2) + ((src_pts[1][1] - src_pts[2][1]) ** 2))
        heightB = np.sqrt(((src_pts[0][0] - src_pts[3][0]) ** 2) + ((src_pts[0][1] - src_pts[3][1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Define the destination points (a perfect flat rectangle starting at 0,0)
        dst_pts = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # Compute the homography matrix and apply the warp
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped_img = cv2.warpPerspective(img, matrix, (maxWidth, maxHeight))

        # CHANGED: Return the warped image array directly instead of saving it
        return True, warped_img
        
    else:
        print("Could not find all 4 markers. Skipping warp.")
        # CHANGED: Return the original un-warped image so the pipeline doesn't crash
        return False, img

# Runs the pipeline to capture data and pass to the methods above (Missing thermal)
def run_pipeline(temp_rgb_path, final_rgb_path, final_thermal_path):
    # 1. Hardware Capture
    success, payload = capture_raw_images(temp_rgb_path)

    if not success:
        print(f"Hardware Error: {payload}")
        return False, [] # Return an empty BOM on failure
    
    raw_rgb_file = payload["rgb_path"]
    raw_thermal_data = payload["thermal_raw"]
    
    # 2. ArUco Alignment & Flattening
    # We catch the warped image array returned by your updated function
    warp_success, flattened_image = process_and_flatten_image(raw_rgb_file, final_rgb_path)
    
    # 3. YOLO Component Detection
    # Pass the flattened image array directly to your AI model
    annotated_image, bom_list = pcb_analyzer.analyze_board(flattened_image)

    # 4. Save the final image for the Flask UI to display
    cv2.imwrite(str(final_rgb_path), annotated_image)
    
    # 5. Thermal Processing (Commented out until you are ready for it)
    # process_thermal_data(raw_thermal_data, final_thermal_path)
    
    # Return True and the Bill of Materials back to your Flask app!
    return True, bom_list

# End of Methods ----------------------------------------------------------------------------------------

