import cv2
import json
import os
import numpy as np


def load_path(filename='path.json', marker_id=None):
    """Load trajectory from JSON file
    
    Args:
        filename: Path to JSON file
        marker_id: Specific marker ID to load path for (None for old format)
    
    Returns:
        tuple: (path, device_id) or (path, None) for old format
    """
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            
            # New format with multiple robots
            if 'robots' in data and marker_id is not None:
                marker_str = str(marker_id)
                if marker_str in data['robots']:
                    robot_data = data['robots'][marker_str]
                    return robot_data.get('path', []), robot_data.get('device_id')
                return [], None
            
            # Old format
            return data.get('path', []), None
    except Exception as e:
        print(f"Error loading path: {e}")
        return [], None


def draw_trajectory(frame, path, target_idx=None):
    """
    Draw trajectory points on frame in white, with target waypoint in green
    
    Args:
        frame: Image frame
        path: List of (x, y) waypoints
        target_idx: Index of the current target waypoint (highlighted in green)
    """
    for i, (x, y) in enumerate(path):
        if i == target_idx:
            # Target waypoint in green
            cv2.circle(frame, (int(x), int(y)), 6, (0, 255, 0), -1)
        else:
            # Other waypoints in white
            cv2.circle(frame, (int(x), int(y)), 4, (255, 255, 255), -1)
    return frame


def draw_robot_arrow(frame, center_x, center_y, orientation_rad, length=50):
    """
    Draw a red arrow showing the robot's front direction
    
    Args:
        frame: Image frame
        center_x: Robot center x coordinate
        center_y: Robot center y coordinate
        orientation_rad: Robot orientation in radians
        length: Length of the arrow
    """
    # Calculate arrow end point
    end_x = int(center_x + length * np.cos(orientation_rad))
    end_y = int(center_y + length * np.sin(orientation_rad))
    
    # Draw arrow
    cv2.arrowedLine(frame, 
                    (int(center_x), int(center_y)), 
                    (end_x, end_y), 
                    (0, 0, 255),  # Red color in BGR
                    3,  # Thickness
                    tipLength=0.3)
    
    return frame
