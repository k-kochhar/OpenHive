import pygame
import math
import numpy as np
import json
import os
from robot import Robot
from motion_controller import ManualController, AutonomousController

# Initialize Pygame
pygame.init()

# Constants
ROBOT_START_X = 100
ROBOT_START_Y = 500
ROBOT_START_ANGLE = 0  # Facing right

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (59, 55, 52)

def load_path(filename):
    """Load path from JSON file"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get('waypoints', [])
    except FileNotFoundError:
        print(f"Path file {filepath} not found")
        return []
    except Exception as e:
        print(f"Error loading path: {e}")
        return []

def draw_path(screen, path, current_idx=None):
    """Draw the path waypoints and lines"""
    if not path:
        return
    
    # Draw lines between waypoints
    if len(path) > 1:
        pygame.draw.lines(screen, (200, 200, 200), False, path, 1)
    
    # Draw waypoints
    for i, (x, y) in enumerate(path):
        if i == current_idx:
            # Current target waypoint - green
            pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 5)
        else:
            # Other waypoints - blue
            pygame.draw.circle(screen, (200, 200, 200), (int(x), int(y)), 5)

def main():
    # Initialize screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    # Initialize robot
    robot = Robot(ROBOT_START_X, ROBOT_START_Y, angle=ROBOT_START_ANGLE)
    
    # Load path and initialize controllers
    path = load_path('path.json')
    manual_controller = ManualController()
    autonomous_controller = AutonomousController(path, robot.x, robot.y)
    
    # Start in autonomous mode
    mode = 'autonomous'
    
    # Run simulation loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_a:
                    # Toggle autonomous mode
                    if mode == 'manual':
                        mode = 'autonomous'
                        autonomous_controller.reset(robot.x, robot.y)
                    else:
                        mode = 'manual'
                        robot.set_wheels(0, 0)
        
        # Get control inputs based on mode
        if mode == 'manual':
            keys = pygame.key.get_pressed()
            key_dict = {
                'forward': keys[pygame.K_f],
                'left': keys[pygame.K_l],
                'right': keys[pygame.K_r],
                'stop': keys[pygame.K_s]
            }
            left, right = manual_controller.compute_wheel_speeds(robot, key_dict)
            robot.set_wheels(left, right)
        else:
            left, right = autonomous_controller.compute_wheel_speeds(robot)
            robot.set_wheels(left, right)
        
        # Update robot
        robot.update(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Draw
        screen.fill(BACKGROUND_COLOR)
        
        # Draw path if in autonomous mode
        if mode == 'autonomous':
            draw_path(screen, path, autonomous_controller.current_waypoint_idx)
        
        robot.draw(screen)
        
        # Simulate camera and detect markers
        frame = pygame.surfarray.array3d(screen)
        frame = np.transpose(frame, (1, 0, 2))
        robot.detect_marker(frame)
        
        # Display info
        info_lines = [
            f"X: {int(robot.x)}, Y: {int(robot.y)}",
            f"Angle: {math.degrees(robot.detected_angle):.1f}°",

        ]

        # Draw info text
        y_offset = 10
        for line in info_lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()

