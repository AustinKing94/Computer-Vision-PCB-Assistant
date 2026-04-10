import cv2
import cv2.aruco as aruco
import numpy as np
from src.image_capture import capture_raw_images
from src.thermal_processing import capture_thermal_image

# --- ArUco Helpers ---

def find_marker_positions(corners, ids):
    # Uses sum/difference of center coordinates to identify which marker is in each corner
    centers = []
    for marker in corners:
        points = marker.reshape((4, 2))
        center = np.mean(points, axis=0)
        centers.append(center)

    top_left_idx     = min(range(len(centers)), key=lambda i: centers[i][0] + centers[i][1])
    top_right_idx    = max(range(len(centers)), key=lambda i: centers[i][0] - centers[i][1])
    bottom_right_idx = max(range(len(centers)), key=lambda i: centers[i][0] + centers[i][1])
    bottom_left_idx  = min(range(len(centers)), key=lambda i: centers[i][0] - centers[i][1])

    return {
        "top_left":     top_left_idx,
        "top_right":    top_right_idx,
        "bottom_right": bottom_right_idx,
        "bottom_left":  bottom_left_idx
    }


def define_roi(corners, ids, marker_locations):
    """
    Returns the four inner corners of the ArUco markers as the ROI boundary.
    Instead of hardcoding which corner index [0-3] is the inner corner
    (which breaks when markers are rotated on the jig), we find the inner
    corner geometrically: whichever of the 4 corners is closest to the
    image center is the one facing inward toward the PCB.
    """
    # Compute the center of all 4 markers
    all_centers = []
    for marker in corners:
        pts = marker.reshape((4, 2))
        all_centers.append(np.mean(pts, axis=0))
    image_center = np.mean(all_centers, axis=0)

    def inner_corner(marker_idx):
        pts = corners[marker_idx].reshape((4, 2))
        # Pick whichever corner is closest to the image center
        dists = [np.linalg.norm(pt - image_center) for pt in pts]
        return pts[np.argmin(dists)]

    roi_coordinates = []
    roi_coordinates.append(inner_corner(marker_locations["top_left"]))
    roi_coordinates.append(inner_corner(marker_locations["top_right"]))
    roi_coordinates.append(inner_corner(marker_locations["bottom_right"]))
    roi_coordinates.append(inner_corner(marker_locations["bottom_left"]))
    return roi_coordinates


def process_and_flatten_image(input_image_path):
    """
    Reads an image, detects 4 ArUco markers, extracts the ROI,
    performs a perspective warp to flatten it, and returns the result.
    Returns: (warp_succeeded: bool, image: np.ndarray)
    If 4 markers found: (True, warped image)
    If not enough markers: (False, original image) so the pipeline can still continue
    """
    img = cv2.imread(str(input_image_path))
    if img is None:
        print(f"ERROR: Could not read image at {input_image_path}")
        return False, None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE to even out lighting across the image before detection.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)
    parameters = aruco.DetectorParameters()

    # Tuned for angled camera — wider adaptive threshold range catches
    # markers that are perspective distorted
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 53
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.adaptiveThreshConstant = 7

    # Allow more perspective distortion per marker (default is 0.1)
    parameters.perspectiveRemovePixelPerCell = 8
    parameters.perspectiveRemoveIgnoredMarginPerCell = 0.33

    # Subpixel corner refinement for better accuracy at angle
    parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
    parameters.cornerRefinementWinSize = 5
    parameters.cornerRefinementMaxIterations = 30
    parameters.cornerRefinementMinAccuracy = 0.1

    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None and len(ids) >= 4:
        marker_locations = find_marker_positions(corners, ids)
        roi_coordinates  = define_roi(corners, ids, marker_locations)

        src_pts = np.array([
            roi_coordinates[0],  # Top Left
            roi_coordinates[1],  # Top Right
            roi_coordinates[2],  # Bottom Right
            roi_coordinates[3]   # Bottom Left
        ], dtype="float32")

        # Use Pythagorean theorem to find the longest edges for the output dimensions
        widthA  = np.sqrt(((src_pts[2][0] - src_pts[3][0]) ** 2) + ((src_pts[2][1] - src_pts[3][1]) ** 2))
        widthB  = np.sqrt(((src_pts[1][0] - src_pts[0][0]) ** 2) + ((src_pts[1][1] - src_pts[0][1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA  = np.sqrt(((src_pts[1][0] - src_pts[2][0]) ** 2) + ((src_pts[1][1] - src_pts[2][1]) ** 2))
        heightB  = np.sqrt(((src_pts[0][0] - src_pts[3][0]) ** 2) + ((src_pts[0][1] - src_pts[3][1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst_pts = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        matrix     = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped_img = cv2.warpPerspective(img, matrix, (maxWidth, maxHeight))
        return True, warped_img

    else:
        print("WARNING: Could not find 4 ArUco markers. Skipping perspective warp.")
        return False, img


# --- Main Pipeline ---

def run_pipeline(temp_rgb_path, final_rgb_path, final_thermal_path):
    """
    The full capture-process-analyze pipeline:
      1. Capture raw RGB + thermal data from hardware
      2. Flatten the RGB image using ArUco marker perspective warp
      3. Run YOLO detection on the flattened image
      4. Save the annotated RGB image for the dashboard
      5. Save the thermal image for the dashboard toggle
    Returns: (success: bool, bom_list: list)
    """
    # 1. Hardware Capture
    success, payload = capture_raw_images(temp_rgb_path)
    if not success:
        print(f"PIPELINE FAILED at hardware capture: {payload}")
        return False, []

    raw_rgb_file    = payload["rgb_path"]
    raw_thermal_data = payload["thermal_array"]

    # 2. ArUco Flatten
    warp_success, flattened_image = process_and_flatten_image(raw_rgb_file)
    if flattened_image is None:
        print("PIPELINE FAILED: Could not read captured RGB image.")
        return False, []

    # 3. YOLO Detection
    from src.analyzer import PCBAnalyzer
    pcb_analyzer = PCBAnalyzer()
    annotated_image, bom_list = pcb_analyzer.analyze_board(flattened_image)

    # 4. Save annotated RGB image for Flask dashboard
    cv2.imwrite(str(final_rgb_path), annotated_image)

    # 5. Thermal Processing
    thermal_success, thermal_msg = capture_thermal_image(final_thermal_path)
    if not thermal_success:
        # Non-fatal: RGB capture still succeeded, just log the thermal failure
        print(f"WARNING: Thermal capture failed: {thermal_msg}")

    return True, bom_list
