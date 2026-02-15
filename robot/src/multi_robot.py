#!/usr/bin/env python3
"""
Multi-robot launcher script
Runs multiple controller processes for different robots simultaneously
"""

import subprocess
import sys
import time


def main():
    """Launch multiple controller processes"""
    
    # Define robots to control
    robots = [
        {"marker_id": 0, "device_id": "ESP1"},
        {"marker_id": 3, "device_id": "ESP2"},
        {"marker_id": 6, "device_id": "ESP3"}
    ]
    
    processes = []
    
    try:
        print("=" * 60)
        print("Starting Multi-Robot Controller")
        print("=" * 60)
        
        # Launch controller process for each robot
        for robot in robots:
            marker_id = robot["marker_id"]
            device_id = robot["device_id"]
            
            print(f"\n[Launcher] Starting controller for marker {marker_id} -> {device_id}")
            
            cmd = [
                sys.executable, 
                "controller.py",
                "--marker-id", str(marker_id),
                "--device-id", device_id
            ]
            
            # Start process without capturing output (allows OpenCV windows to work)
            process = subprocess.Popen(cmd)
            
            processes.append({
                "process": process,
                "marker_id": marker_id,
                "device_id": device_id
            })
            
            time.sleep(0.5)  # Small delay between starting processes
        
        print("\n" + "=" * 60)
        print(f"All {len(processes)} controllers started!")
        print("Each controller has its own video window")
        print("Press 'q' in any window to stop that controller")
        print("Press Ctrl+C here to stop all controllers")
        print("=" * 60 + "\n")
        
        # Wait for all processes to complete
        for proc_info in processes:
            proc = proc_info["process"]
            proc.wait()
    
    except KeyboardInterrupt:
        print("\n\n[Launcher] Stopping all controllers...")
    
    finally:
        # Terminate all processes
        for proc_info in processes:
            proc = proc_info["process"]
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except:
                proc.kill()
        
        print("[Launcher] All controllers stopped")


if __name__ == "__main__":
    main()

