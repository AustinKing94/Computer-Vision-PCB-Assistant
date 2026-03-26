import cv2
import cv2.aruco as aruco
import numpy as np

# Methods for modularity
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
    
    # Map ids to corners to keep access to coordinates
    marker_locations = {
        ids[top_left_idx][0]: "top_left",
        ids[top_right_idx][0]: "top_right",
        ids[bottom_right_idx][0]: "bottom_right",
        ids[bottom_left_idx][0]: "bottom_left"
    }

    print(marker_locations)
    return marker_locations 



# Read the image
img = cv2.imread('/Users/austinking/Documents/CurrentCourseWork/COMP-4983/finalProject/images/real.png')

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Initialize ArUco detector - PredefinedDictionary must match ArUco markers being used
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Detect markers
corners, ids, rejected = detector.detectMarkers(gray)

# If else checks to make sure markers were detected before processing
if ids is not None:
    # Map position of corners within image (Ex. top_left, bottom_right)
    (find_marker_positions(corners, ids))

    # Outputs detection of markers for debugging
    img_with_markers = aruco.drawDetectedMarkers(img, corners, ids)
    #print(f"Detected {len(ids)} markers with IDs: {ids.flatten()}")
else:
    img_with_markers = img
    #print("No markers detected")

# Display the image
cv2.imshow('ArUco Markers Detection', img_with_markers)
cv2.waitKey(0)
cv2.destroyAllWindows()
