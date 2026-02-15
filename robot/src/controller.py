from utils import Camera, load_path, draw_trajectory, draw_robot_arrow, PathFollower, RobotClient
import cv2
import asyncio
import time


async def main():
    camera = Camera(video_source=0)
    path = load_path()
    
    # Initialize path follower
    path_follower = PathFollower(path)
    path_follower_initialized = False
    
    # Initialize robot client
    robot = RobotClient(host="localhost", port=8765, device_id="CONTROLLER")
    connected = await robot.connect()
    
    if connected:
        print("Connected to robot server")
    else:
        print("Not connected")
    
    last_command_time = time.time()
    command_interval = 0.25
    
    try:
        while True:
            # Get frame and detected markers
            frame, markers = camera.get_markers()
            
            current_command = "S"
            target_idx = None
            robot_info = None
            
            # Process markers for path following
            if markers:
                # Use the first detected marker for control
                marker_id = list(markers.keys())[0]
                info = markers[marker_id]
                
                # Extract robot position and orientation
                robot_x, robot_y = info['center']
                robot_angle_rad = info['orientation_rad']
                robot_info = info
                
                # Initialize path follower on first detection
                if not path_follower_initialized:
                    path_follower.initialize(robot_x, robot_y)
                    path_follower_initialized = True
                
                # Get command for robot (computed every frame)
                current_command = path_follower.get_command(robot_x, robot_y, robot_angle_rad)
                target_idx = path_follower.get_current_waypoint_idx()
                
                # Send command every command_interval seconds
                current_time = time.time()
                if current_time - last_command_time >= command_interval:
                    if connected:
                        await robot.send_command(current_command)
                    print(f"Marker {marker_id}: Pos=({robot_x:.1f}, {robot_y:.1f}), "
                          f"Angle={info['orientation_deg']:.1f}°, Command={current_command}")
                    last_command_time = current_time
            
            # Draw trajectory with target waypoint highlighted
            frame = draw_trajectory(frame, path, target_idx)
            
            # Draw robot arrow if robot detected
            if robot_info:
                frame = draw_robot_arrow(frame, robot_info['center'][0], 
                                        robot_info['center'][1], 
                                        robot_info['orientation_rad'])
            
            # Display video feed
            cv2.imshow('Robot Controller', frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Small delay to prevent busy loop
            await asyncio.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\n[Exiting]")
    
    finally:
        # Send stop command before disconnecting
        if connected:
            await robot.send_command("S")
        await robot.disconnect()
        camera.release()


if __name__ == "__main__":
    asyncio.run(main())
