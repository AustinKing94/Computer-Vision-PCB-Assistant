import cv2
import cv2.aruco as aruco
import numpy as np

# Methods for modularity
# Uses sum and difference to calculate which marker is in each corner of the image
def find_marker_positions(corners):
    # Initialize arrays for sum and diff of initial point on marker (always top left of each marker)
    sum_array = np.empty(4)
    diff_array = np.empty(4)

    # Loops through array of markers
    for i, marker in enumerate(corners): 
        points = marker.reshape((4, 2)) # Convert to 4 rows and 2 columns
        #print(f"index: {i}, value: {points}")

        sum_array[i] = (np.sum(points[0]))
        diff_array[i] = (np.diff(points[0]))

    print(sum_array) 
    print(diff_array)
            
    marker_locations = {
        "top_left": (min(sum_array)),
        "top_right": (max(diff_array)),
        "bottom_right": (max(sum_array)),
        "bottom_left": (min(diff_array))
    }
    return marker_locations

# Read the image
img = cv2.imread('/Users/austinking/Documents/CurrentCourseWork/COMP-4983/finalProject/images/aruco.png')

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
    (find_marker_positions(corners))

    # Outputs detection of markers for debugging
    img_with_markers = aruco.drawDetectedMarkers(img, corners, ids)
    #print(f"Detected {len(ids)} markers with IDs: {ids.flatten()}")
else:
    img_with_markers = img
    #print("No markers detected")

# Display the image
#cv2.imshow('ArUco Markers Detection', img_with_markers)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
