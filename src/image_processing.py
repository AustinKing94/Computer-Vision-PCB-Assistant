import cv2
import cv2.aruco as aruco
import numpy as np

# Methods for modularity --------------------------------------------------------
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

# Uses roi coordincates to do perspective transformation and pixel to mm mapping


# End of Methods ---------------------------------------------------------------------------------------

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
    marker_locations = find_marker_positions(corners, ids)

    # Define ROI
    roi_coordinates = define_roi(corners, ids, marker_locations)

    # Outputs detection of markers and roi for debugging
    img_with_markers = aruco.drawDetectedMarkers(img, corners, ids)

    '''top_left_point = (roi_coordinates[0]) # Gets point from roi coords
    top_left_point = tuple(map(int, top_left_point)) # Converts numpy float to tuple of ints for cv2
    top_right_point = (roi_coordinates[1]) # Gets point from roi coords
    top_right_point = tuple(map(int, top_right_point)) # Converts numpy float to tuple of ints for cv2
    bottom_right_point = (roi_coordinates[2]) # Gets point from roi coords
    bottom_right_point = tuple(map(int, bottom_right_point)) # Converts numpy float to tuple of ints for cv2
    bottom_left_point = (roi_coordinates[3]) # Gets point from roi coords
    bottom_left_point = tuple(map(int, bottom_left_point)) # Converts numpy float to tuple of ints for cv2'''

else:
    img_with_markers = img
    print("No markers detected")

# Display the image
cv2.imshow('ArUco Markers Detection', img_with_markers)
cv2.waitKey(0)
cv2.destroyAllWindows()
