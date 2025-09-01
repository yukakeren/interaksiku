# Hand tracking and gesture recognition
import cv2
import numpy as np
import math
from typing import Optional, Tuple, List
from config import HAND_TRACKING

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None
    print("Warning: mediapipe not available. Hand tracking will not work.")


class HandTracker:
    """Handles hand tracking and gesture recognition"""
    
    def __init__(self):
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
        else:
            self.mp_hands = None
            self.mp_drawing = None
        self.hands = None
        
    def initialize(self) -> None:
        """Initialize MediaPipe hands"""
        if MEDIAPIPE_AVAILABLE and self.mp_hands:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=HAND_TRACKING['max_num_hands'],
                min_detection_confidence=HAND_TRACKING['min_detection_confidence'],
                min_tracking_confidence=HAND_TRACKING['min_tracking_confidence']
            )
    
    def process_frame(self, frame: np.ndarray):
        """
        Process frame and detect hand landmarks
        
        Args:
            frame: Input frame
            
        Returns:
            Hand landmarks or None if no hand detected
        """
        if not self.hands or not MEDIAPIPE_AVAILABLE:
            return None
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        if results.multi_hand_landmarks:
            return results.multi_hand_landmarks[0]  # Return first hand
        return None
    
    def draw_landmarks(self, frame: np.ndarray, landmarks) -> None:
        """Draw hand landmarks on frame"""
        if self.mp_drawing and landmarks and MEDIAPIPE_AVAILABLE:
            self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
    
    def get_hand_center(self, landmarks, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """
        Get hand center position (middle finger MCP)
        
        Args:
            landmarks: Hand landmarks
            frame_width: Frame width
            frame_height: Frame height
            
        Returns:
            Center coordinates (x, y)
        """
        if not landmarks:
            return 0, 0
        lm = landmarks.landmark[9]  # Middle finger MCP
        return int(lm.x * frame_width), int(lm.y * frame_height)
    
    def is_hand_closed(self, landmarks) -> bool:
        """
        Detect if hand is closed (fist gesture for clicking)
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            True if hand is closed, False otherwise
        """
        if not landmarks:
            return False
            
        # Get middle finger MCP and tip
        lm9 = landmarks.landmark[9]   # Middle finger MCP
        lm12 = landmarks.landmark[12] # Middle finger tip
        
        # Calculate distance between MCP and tip
        distance = math.sqrt((lm12.x - lm9.x)**2 + (lm12.y - lm9.y)**2)
        
        # Hand is considered closed if distance is below threshold
        return distance < HAND_TRACKING['click_distance_threshold']
    
    def is_position_stable(self, current_pos: Tuple[int, int], last_pos: Optional[Tuple[int, int]]) -> bool:
        """
        Check if hand position is stable for calibration
        
        Args:
            current_pos: Current hand position
            last_pos: Last recorded position
            
        Returns:
            True if position is stable, False otherwise
        """
        if last_pos is None:
            return False
        
        threshold = HAND_TRACKING['stability_threshold']
        return (abs(current_pos[0] - last_pos[0]) < threshold and 
                abs(current_pos[1] - last_pos[1]) < threshold)
    
    def close(self) -> None:
        """Clean up resources"""
        if self.hands:
            self.hands.close()
            self.hands = None


class PositionSmoother:
    """Handles mouse position smoothing"""
    
    def __init__(self, smoothing_factor: int = 5):
        self.smoothing_factor = smoothing_factor
        self.prev_positions_x: List[int] = []
        self.prev_positions_y: List[int] = []
    
    def add_position(self, x: int, y: int) -> Tuple[int, int]:
        """
        Add new position and return smoothed coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Smoothed coordinates (x, y)
        """
        self.prev_positions_x.append(x)
        self.prev_positions_y.append(y)
        
        # Keep only recent positions
        if len(self.prev_positions_x) > self.smoothing_factor:
            self.prev_positions_x.pop(0)
            self.prev_positions_y.pop(0)
        
        # Return smoothed position
        if self.prev_positions_x:
            smoothed_x = int(sum(self.prev_positions_x) / len(self.prev_positions_x))
            smoothed_y = int(sum(self.prev_positions_y) / len(self.prev_positions_y))
            return smoothed_x, smoothed_y
        
        return x, y
    
    def reset(self) -> None:
        """Reset position history"""
        self.prev_positions_x.clear()
        self.prev_positions_y.clear()
    
    def set_smoothing_factor(self, factor: int) -> None:
        """Update smoothing factor"""
        self.smoothing_factor = factor
