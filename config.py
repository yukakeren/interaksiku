# Configuration constants and settings
import os

# UI Constants
WINDOW_TITLE = "Ultimate Comfis Mouse - Calibration & Control"
WINDOW_GEOMETRY = "1000x700"
HEADER_HEIGHT = 80
LEFT_PANEL_WIDTH = 350

# Colors
COLORS = {
    'primary': "#2c3e50",
    'secondary': "#3498db",
    'success': "#27ae60",
    'danger': "#e74c3c",
    'warning': "#f39c12",
    'light': "#ecf0f1",
    'background': "#f0f0f0",
    'white': "white",
    'black': "black"
}

# Fonts
FONTS = {
    'title': ("Arial", 20, "bold"),
    'subtitle': ("Arial", 12),
    'heading': ("Arial", 12, "bold"),
    'normal': ("Arial", 10),
    'small': ("Arial", 9),
    'button': ("Arial", 11)
}

# Camera settings
CAMERA_SETTINGS = {
    'default_width': 640,
    'default_height': 480,
    'default_fps': 30,
    'max_camera_check': 10
}

# Hand tracking settings
HAND_TRACKING = {
    'max_num_hands': 1,
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.7,
    'click_distance_threshold': 0.05,
    'stability_threshold': 20,
    'stability_frames': 30
}

# Calibration settings
CALIBRATION = {
    'corner_names': ["Top Left", "Top Right", "Bottom Right", "Bottom Left"],
    'point_radius': 12,
    'canvas_width': 640,
    'canvas_height': 480,
    'default_points': [[100, 100], [540, 100], [540, 380], [100, 380]]
}

# File paths
FILES = {
    'calibration_points': "calibration_points.npy",
    'calibration_method': "calibration_method.txt",
    'calibration_flip': "calibration_flip.txt"
}

# Environment setup
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
