import pygame
import math
import numpy as np
from robot import Robot

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (59, 55, 52)

def main():
    # Initialize screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    # Initialize robot
    robot = Robot(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, angle=0)
    
    # Run simulation loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_f]:
            # Forward: both wheels forward
            robot.set_wheels(100, 100)
        elif keys[pygame.K_l]:
            # Left: left wheel backward, right wheel forward
            robot.set_wheels(-100, 100)
        elif keys[pygame.K_r]:
            # Right: left wheel forward, right wheel backward
            robot.set_wheels(100, -100)
        elif keys[pygame.K_s]:
            # Stop: both wheels stopped
            robot.set_wheels(0, 0)
        
        # Update robot
        robot.update(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Draw
        screen.fill(BACKGROUND_COLOR)
        robot.draw(screen)
        
        # Simulate camera and detect markers
        frame = pygame.surfarray.array3d(screen)
        frame = np.transpose(frame, (1, 0, 2))
        robot.detect_marker(frame)
        
        # Display info
        info_lines = [
            f"X: {int(robot.x)}, Y: {int(robot.y)}",
            f"Angle: {math.degrees(robot.detected_angle):.1f}°"
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
