```json
{
  "world": {
    "name": "ArUco Vision Swarm",
    "description": "Physical robot swarm tracked via overhead camera using ArUco markers. Robots operate in a 2D plane with pixel-based coordinates from camera feed. Movement planning uses neural pathfinding with color-based obstacle detection (green, blue, and black objects detected as obstacles).",
    "boundaries": {
      "shape": "rectangle",
      "dimensions": {
        "width_px": 640,
        "height_px": 480,
        "note": "Pixel dimensions from camera frame; actual physical size unknown"
      },
      "origin": "[0, 0] — top-left corner of camera frame, x increases rightward, y increases downward"
    }
  },

  "agents": {
    "count": 3,
    "types": [
      {
        "type_id": "default",
        "count": 3,
        "physical": {
          "size": {
            "note": "Physical dimensions not specified",
            "footprint_cells": 4,
            "footprint_description": "4-cell radius clearance maintained in 32x32 grid"
          },
          "speed_max": null,
          "battery_life": null,
          "weight_capacity": null
        },
        "sensors": [
          "aruco_marker",
          "overhead_camera_tracking"
        ],
        "actuators": [
          "differential_drive",
          "pusher"
        ]
      }
    ]
  },

  "actions": {
    "built_in": [
      "move_to(x, y) — navigate agent to target coordinates (handled by path planner)",
      "stop() — halt agent immediately"
    ],
    "extra": [
      {
        "name": "push_and_exit",
        "description": "Three-step obstacle removal: (1) navigate to nearest obstacle using neural A* pathfinding, (2) align to face obstacle, (3) drive straight through obstacle to nearest boundary edge, pushing it off the playing field",
        "requires": ["differential_drive", "pusher", "overhead_camera_tracking"],
        "parameters": ["bot_id — which robot executes the push (0, 1, or 2)"]
      },
      {
        "name": "get_orientation_coordinates",
        "description": "Query current pixel position and orientation (degrees and radians) of one or all robots from live camera feed",
        "requires": ["overhead_camera_tracking", "aruco_marker"],
        "parameters": ["bot_id — target robot (0, 1, or 2), or None for all robots"]
      }
    ]
  },

  "obstacles": {
    "known_types": [
      {
        "type": "colored_object",
        "typical_size": {
          "note": "Detected via HSV color thresholding",
          "colors": ["green", "blue", "black"]
        },
        "movable": true,
        "frequency": "common"
      }
    ],
    "static_obstacles": [],
    "dynamic_obstacles_expected": true
  },

  "missions": {
    "type": "user_input",
    "config": {
      "user_input": {
        "enabled": true,
        "description": "User issues real-time commands to control individual robots. Each command targets a specific bot (0, 1, or 2) and the system executes immediately. Camera provides live feedback via screenshot attachment with each task.",
        "examples": [
          "Move bot 0 to pixel position [320, 240]",
          "Get current positions of all robots",
          "Bot 1 push the nearest obstacle off the field",
          "Stop bot 2",
          "Move bot 0 to the center, then have bot 1 push the blue obstacle out"
        ]
      },
      "bot_controlled": {
        "enabled": false,
        "description": null,
        "trigger": {
          "type": null,
          "interval_seconds": null,
          "condition": null
        },
        "response": null,
        "examples": []
      }
    }
  },

  "rules": [
    "Always call get_orientation_coordinates(bot_id=None) before planning movements to get current robot positions",
    "Multiple robots can move in parallel — the system handles concurrent movement coordination",
    "Bots maintain a 4-cell radius clearance zone in the obstacle detection grid to prevent self-collision",
    "Pixel coordinate system: origin at top-left, x increases right, y increases down",
    "Valid bot IDs are 0, 1, and 2 (mapped internally to ArUco markers 0, 3, and 6)",
    "Neural pathfinding with A* heuristic is used for obstacle avoidance during move_to operations",
    "Obstacles detected via color thresholding: green (HSV 35-85), blue (HSV 100-130), black (value <50)",
    "Camera screenshot is provided with each task request showing current world state",
    "Push operations use three phases: navigate (obstacle-aware), align (face target), march (straight through)",
    "Path planning operates on 32x32 grid for detection, scaled to 64x64 for neural pathfinding",
    "If pathfinding fails, system falls back to straight-line waypoint generation",
    "WebSocket communication to ESP devices may fail gracefully — bots run open-loop if connection is lost",
    "Stop commands immediately halt movement threads and clear active bot registry"
  ],

  "assumptions": [
    "Camera frame dimensions assumed to be 640x480 pixels (fallback values if screenshot unavailable)",
    "Physical dimensions of robots unknown — represented as 4-cell clearance radius in 32x32 grid (~5% of frame width)",
    "Robot speed, battery life, and weight capacity not specified — assumed managed externally or irrelevant to this session",
    "ArUco marker IDs 0, 3, and 6 correspond to bots 0, 1, and 2 respectively (as specified in code)",
    "Obstacle colors (green, blue, black) are the only objects to avoid — other colors treated as free space",
    "Boundary edges are frame edges (x=0, x=width, y=0, y=height) — no physical walls defined",
    "ESP device IDs are ESP1, ESP2, ESP3 mapped to bots 0, 1, 2",
    "WebSocket server runs on localhost:8765 for robot communication",
    "Overlay.py process writes markers.json with live tracking data — assumed to be running concurrently",
    "Neural pathfinding checkpoint file exists at move_world/checkpoints/best_model.pt",
    "No battery management or return-to-base behavior specified — assumed unlimited operation or external recharging",
    "Screenshot attachment format is PNG bytes — provided with each task by the framework",
    "Grid overlay uses 32x32 cells for human reference but internal pathfinding uses 64x64 resolution"
  ]
}
```