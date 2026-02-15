import math


class PathFollower:
    """Path following controller that returns simple movement commands"""
    
    def __init__(self, path, waypoint_threshold=40, angle_threshold=0.4):
        """
        Args:
            path: List of (x, y) waypoint tuples
            waypoint_threshold: Distance at which a waypoint is considered reached
            angle_threshold: Angle error threshold (radians) to start moving forward (0.4 rad ≈ 23°)
        """
        self.path = path
        self.waypoint_threshold = waypoint_threshold
        self.angle_threshold = angle_threshold
        self.current_waypoint_idx = 0
        self.finished = False
    
    def initialize(self, robot_x, robot_y):
        """
        Initialize the controller by finding the closest waypoint
        
        Args:
            robot_x: Robot x position
            robot_y: Robot y position
        """
        if not self.path:
            return
        
        # Find closest waypoint to robot's initial position
        closest_idx, closest_dist = self._find_closest_waypoint_with_distance(robot_x, robot_y)
        
        # If already at the closest waypoint, target the next one
        if closest_dist < self.waypoint_threshold:
            self.current_waypoint_idx = (closest_idx + 1) % len(self.path)
        else:
            # Otherwise, navigate to the closest waypoint first
            self.current_waypoint_idx = closest_idx
    
    def get_command(self, robot_x, robot_y, robot_angle_rad):
        """
        Get movement command based on robot position and orientation
        
        Args:
            robot_x: Robot x position
            robot_y: Robot y position
            robot_angle_rad: Robot orientation in radians
        
        Returns:
            str: Command - "F" (forward), "L" (left), "R" (right), "S" (stop)
        """
        if not self.path:
            return "S"
        
        # Check if robot is at the last waypoint - if so, stop
        last_waypoint_x, last_waypoint_y = self.path[-1]
        dist_to_end = math.sqrt((last_waypoint_x - robot_x)**2 + (last_waypoint_y - robot_y)**2)
        
        if dist_to_end < self.waypoint_threshold:
            self.finished = True
            self.current_waypoint_idx = len(self.path) - 1
            return "S"
        
        # Otherwise, ensure we're following the path
        self.finished = False
        
        # Get current target waypoint
        if self.current_waypoint_idx >= len(self.path):
            self.current_waypoint_idx = len(self.path) - 1
            
        target_x, target_y = self.path[self.current_waypoint_idx]
        
        # Calculate distance to current target waypoint
        dx = target_x - robot_x
        dy = target_y - robot_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if waypoint reached
        if distance < self.waypoint_threshold:
            self.current_waypoint_idx += 1
            if self.current_waypoint_idx >= len(self.path):
                # At the end
                self.finished = True
                return "S"
            # Get next waypoint
            target_x, target_y = self.path[self.current_waypoint_idx]
            dx = target_x - robot_x
            dy = target_y - robot_y
        else:
            # Check if robot has deviated - find closest waypoint ahead on path
            closest_idx, _ = self._find_closest_waypoint_with_distance(robot_x, robot_y)
            # Only update if the closest waypoint is ahead or if we're significantly off course
            if closest_idx > self.current_waypoint_idx or distance > self.waypoint_threshold * 3:
                self.current_waypoint_idx = closest_idx
                target_x, target_y = self.path[self.current_waypoint_idx]
                dx = target_x - robot_x
                dy = target_y - robot_y
        
        # Calculate desired angle to target
        target_angle = math.atan2(dy, dx)
        
        # Calculate angle error (normalize to -pi to pi)
        angle_error = target_angle - robot_angle_rad
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi
        
        # Two-state control: rotate then drive
        if abs(angle_error) > self.angle_threshold:
            # Not aligned: rotate in place
            if angle_error > 0:
                return "R"  # Turn right
            else:
                return "L"  # Turn left
        else:
            # Aligned: drive straight forward
            return "F"
    
    def get_current_waypoint_idx(self):
        """Get the index of the current target waypoint"""
        if self.finished or self.current_waypoint_idx >= len(self.path):
            return None
        return self.current_waypoint_idx
    
    def get_current_waypoint(self):
        """Get the current target waypoint coordinates"""
        if self.finished or self.current_waypoint_idx >= len(self.path):
            return None
        return self.path[self.current_waypoint_idx]
    
    def _find_closest_waypoint_with_distance(self, robot_x, robot_y):
        """Find the index and distance of the closest waypoint to the given position"""
        min_dist = float('inf')
        closest_idx = 0
        
        for i, (wx, wy) in enumerate(self.path):
            dist = math.sqrt((wx - robot_x)**2 + (wy - robot_y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
        
        return closest_idx, min_dist
