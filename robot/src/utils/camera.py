import cv2
import numpy as np
from cv2 import aruco


class Camera:
    """
    Camera class for ArUco marker detection.
    """
    
    def __init__(self, video_source=0, marker_id=None):
        """
        Initialize camera with ArUco detector
        
        Args:
            video_source: Camera index (0 for default) or video file path
            marker_id: Specific marker ID to track (None for all markers)
        """
        self.marker_id = marker_id
        self.video_source = video_source
        self.cap = cv2.VideoCapture(video_source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Error: Could not open video source {video_source}")
        
        # Use ARUCO_ORIGINAL dictionary
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
        
        # Set up detector parameters
        parameters = aruco.DetectorParameters()
        parameters.adaptiveThreshWinSizeMin = 3
        parameters.adaptiveThreshWinSizeMax = 53
        parameters.adaptiveThreshWinSizeStep = 4
        parameters.adaptiveThreshConstant = 7
        parameters.minMarkerPerimeterRate = 0.01
        parameters.maxMarkerPerimeterRate = 8.0
        parameters.polygonalApproxAccuracyRate = 0.1
        parameters.minCornerDistanceRate = 0.01
        parameters.minDistanceToBorder = 1
        parameters.minMarkerDistanceRate = 0.01
        parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
        parameters.cornerRefinementWinSize = 5
        parameters.cornerRefinementMaxIterations = 50
        parameters.cornerRefinementMinAccuracy = 0.01
        
        # Create detector
        self.detector = aruco.ArucoDetector(aruco_dict, parameters)
    
    def get_markers(self):
        """
        Capture frame and detect all ArUco markers
        
        Returns:
            tuple: (frame, markers) where:
                - frame: BGR image frame (or None if capture failed)
                - markers: Dictionary mapping marker IDs to their info:
                    {
                        marker_id: {
                            'center': (x, y),
                            'orientation_deg': float,
                            'orientation_rad': float
                        }
                    }
        """
        ret, frame = self.cap.read()
        
        if not ret:
            return None, {}
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect markers
        corners, ids, _ = self.detector.detectMarkers(gray)
        
        markers = {}
        
        if ids is not None:
            for corner, marker_id in zip(corners, ids):
                marker_id = int(marker_id[0])
                
                # Calculate center
                center = corner[0].mean(axis=0)
                center_x, center_y = float(center[0]), float(center[1])
                
                # Calculate orientation angle from top edge (corner 0 to corner 1)
                top_left = corner[0][0]
                top_right = corner[0][1]
                angle_rad = np.arctan2(top_right[1] - top_left[1], top_right[0] - top_left[0])
                
                # Adjust for robot's actual front being 90 degrees to the right
                angle_rad += np.pi / 2
                
                angle_deg = np.degrees(angle_rad)
                
                # Only include if no filter or matches filter
                if self.marker_id is None or marker_id == self.marker_id:
                    markers[marker_id] = {
                        'center': (center_x, center_y),
                        'orientation_deg': float(angle_deg),
                        'orientation_rad': float(angle_rad)
                    }
        
        return frame, markers
    
    def release(self):
        """Release camera resources"""
        self.cap.release()
        cv2.destroyAllWindows()
