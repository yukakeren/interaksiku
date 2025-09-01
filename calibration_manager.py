# Calibration management
import cv2
import numpy as np
import os
from typing import List, Tuple, Optional
from config import CALIBRATION, FILES


class CalibrationManager:
    """Handles calibration data and perspective transformation"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.calibration_points: List[List[int]] = []
        self.calibration_matrix: Optional[np.ndarray] = None
        self.calibration_method = "manual"
        self.use_flip = False
    
    def set_calibration_points(self, points: List[List[int]]) -> None:
        """Set calibration points and update transformation matrix"""
        self.calibration_points = points
        self._setup_transformation_matrix()
    
    def add_calibration_point(self, point: List[int]) -> None:
        """Add a calibration point"""
        self.calibration_points.append(point)
        if len(self.calibration_points) == 4:
            self._setup_transformation_matrix()
    
    def clear_calibration_points(self) -> None:
        """Clear all calibration points"""
        self.calibration_points.clear()
        self.calibration_matrix = None
    
    def is_calibrated(self) -> bool:
        """Check if calibration is complete"""
        return len(self.calibration_points) == 4 and self.calibration_matrix is not None
    
    def transform_point(self, point: Tuple[int, int]) -> Tuple[int, int]:
        """
        Transform camera coordinates to screen coordinates
        
        Args:
            point: Camera coordinates (x, y)
            
        Returns:
            Screen coordinates (x, y)
        """
        if not self.is_calibrated():
            return point
        
        # Transform point using perspective transformation
        hand_point = np.array([[point[0], point[1]]], dtype=np.float32).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(hand_point, self.calibration_matrix)[0][0]
        
        # Keep within screen bounds
        mapped_x = max(0, min(self.screen_width - 1, int(transformed[0])))
        mapped_y = max(0, min(self.screen_height - 1, int(transformed[1])))
        
        return mapped_x, mapped_y
    
    def _setup_transformation_matrix(self) -> None:
        """Set up perspective transformation matrix"""
        if len(self.calibration_points) == 4:
            screen_corners = np.float32([
                [0, 0],
                [self.screen_width, 0],
                [self.screen_width, self.screen_height],
                [0, self.screen_height]
            ])
            self.calibration_matrix = cv2.getPerspectiveTransform(
                np.float32(self.calibration_points),
                screen_corners
            )
    
    def save_calibration(self, method: str, flip_setting: bool) -> bool:
        """
        Save calibration to files
        
        Args:
            method: Calibration method used
            flip_setting: Whether flip was enabled
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_calibrated():
                return False
            
            # Save calibration points
            np.save(FILES['calibration_points'], np.array(self.calibration_points))
            
            # Save method
            method_name = "gui_manual" if method == "manual" else "opencv_hand_tracking"
            with open(FILES['calibration_method'], "w") as f:
                f.write(method_name)
            
            # Save flip setting
            with open(FILES['calibration_flip'], "w") as f:
                f.write("true" if flip_setting else "false")
            
            self.calibration_method = method
            self.use_flip = flip_setting
            
            return True
        except Exception as e:
            print(f"Error saving calibration: {e}")
            return False
    
    def load_calibration(self) -> bool:
        """
        Load calibration from files
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(FILES['calibration_points']):
                return False
            
            # Load calibration points
            self.calibration_points = np.load(FILES['calibration_points']).tolist()
            
            # Load method
            if os.path.exists(FILES['calibration_method']):
                with open(FILES['calibration_method'], "r") as f:
                    method = f.read().strip()
                    self.calibration_method = "manual" if method == "gui_manual" else "opencv"
            
            # Load flip setting
            if os.path.exists(FILES['calibration_flip']):
                with open(FILES['calibration_flip'], "r") as f:
                    flip_setting = f.read().strip()
                    self.use_flip = flip_setting.lower() == "true"
            
            # Set up transformation matrix
            self._setup_transformation_matrix()
            
            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False
    
    def draw_calibration_area(self, frame: np.ndarray) -> None:
        """Draw calibration area on frame"""
        if len(self.calibration_points) == 4:
            points = np.array(self.calibration_points, dtype=np.int32)
            cv2.polylines(frame, [points], True, (0, 255, 255), 2)
            
            # Add labels for calibration corners
            corner_labels = ["TL", "TR", "BR", "BL"]
            for i, (point, label) in enumerate(zip(self.calibration_points, corner_labels)):
                cv2.circle(frame, tuple(map(int, point)), 5, (0, 255, 255), -1)
                cv2.putText(frame, label, (int(point[0]) + 10, int(point[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)


class ManualCalibration:
    """Handles manual calibration with drag-and-drop interface"""
    
    def __init__(self, canvas_width: int = 640, canvas_height: int = 480):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.points = CALIBRATION['default_points'].copy()
        self.point_radius = CALIBRATION['point_radius']
        self.selected_point = -1
        self.dragging = False
    
    def find_closest_point(self, x: int, y: int) -> int:
        """
        Find closest point to given coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Index of closest point or -1 if none found
        """
        min_dist = float('inf')
        closest_point = -1
        
        for i, point in enumerate(self.points):
            dist = np.sqrt((x - point[0])**2 + (y - point[1])**2)
            if dist < min_dist and dist <= self.point_radius + 5:
                min_dist = dist
                closest_point = i
        
        return closest_point
    
    def update_point(self, index: int, x: int, y: int) -> None:
        """Update point position within bounds"""
        if 0 <= index < len(self.points):
            # Keep within bounds
            x = max(20, min(self.canvas_width - 20, x))
            y = max(20, min(self.canvas_height - 20, y))
            self.points[index] = [x, y]
    
    def get_points(self) -> List[List[int]]:
        """Get current calibration points"""
        return self.points.copy()
