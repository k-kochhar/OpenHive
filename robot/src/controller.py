from utils import Camera, load_path, draw_trajectory, draw_robot_arrow, PathFollower, RobotClient
import cv2
import asyncio
import time
import argparse


async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Robot Controller')
    parser.add_argument('--marker-id', type=int, required=True, help='ArUco marker ID to track')
    parser.add_argument('--device-id', type=str, required=True, help='Target device ID (e.g., ESP1, ESP2)')
    args = parser.parse_args()
    
    marker_id = args.marker_id
    device_id = args.device_id
    
    print(f"[Controller] Tracking marker {marker_id} for device {device_id}")
    
    # Initialize camera with marker filter
    camera = Camera(video_source=0, marker_id=marker_id)
    
    # Load path for this specific robot
    path, loaded_device_id = load_path(marker_id=marker_id)
    
    if not path:
        print(f"Error: No path found for marker {marker_id}")
        return
    
    print(f"[Controller] Loaded {len(path)} waypoints for marker {marker_id}")
    
    # Initialize path follower
    path_follower = PathFollower(path)
    path_follower_initialized = False
    
    # Initialize robot client with specific target
    robot = RobotClient(
        host="localhost", 
        port=8765, 
        device_id=f"CONTROLLER_{marker_id}",
        target_device=device_id
    )
    connected = await robot.connect()
    
    if connected:
        print("Connected to robot server")
    else:
        print("Not connected")
    
    last_command_time = time.time()
    command_interval = 0.5
    
    try:
        while True:
            # Get frame and detected markers
            frame, markers = camera.get_markers()
            
            current_command = "S"
            target_idx = None
            robot_info = None
            
            # Process markers for path following
            if markers:
                # Get info for the tracked marker
                info = markers.get(marker_id)
                
                if info:
                    # Extract robot position and orientation
                    robot_x, robot_y = info['center']
                    robot_angle_rad = info['orientation_rad']
                    robot_info = info
                    
                    # Initialize path follower on first detection
                    if not path_follower_initialized:
                        path_follower.initialize(robot_x, robot_y)
                        path_follower_initialized = True
                    
                    target_idx = path_follower.get_current_waypoint_idx()
                    
                    # Get command from path follower
                    current_command = path_follower.get_command(robot_x, robot_y, robot_angle_rad)
                    
                    # Send command based on interval
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
            cv2.imshow(f'Robot Controller - Marker {marker_id} ({device_id})', frame)
            
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
