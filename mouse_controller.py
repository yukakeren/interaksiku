# Mouse control functionality
import time
from typing import Tuple, Optional
try:
    from pynput.mouse import Controller, Button
except ImportError:
    print("Warning: pynput not available. Mouse control will not work.")
    Controller = None
    Button = None

from hand_tracker import HandTracker, PositionSmoother
from calibration_manager import CalibrationManager


class MouseController:
    """Handles mouse control using hand tracking"""
    
    def __init__(self, calibration_manager: CalibrationManager):
        self.calibration_manager = calibration_manager
        self.mouse = Controller() if Controller else None
        self.hand_tracker = HandTracker()
        self.position_smoother = PositionSmoother()
        self.is_clicking = False
        
    def initialize(self) -> bool:
        """Initialize mouse controller"""
        if not self.mouse:
            print("Mouse controller not available")
            return False
        
        self.hand_tracker.initialize()
        return True
    
    def process_frame(self, frame, smoothing_factor: int = 5) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Process frame for mouse control
        
        Args:
            frame: Input frame
            smoothing_factor: Smoothing factor for mouse movement
            
        Returns:
            Tuple of (hand_detected, screen_coordinates)
        """
        if not self.mouse or not self.calibration_manager.is_calibrated():
            return False, None
        
        # Update smoothing factor
        self.position_smoother.set_smoothing_factor(smoothing_factor)
        
        # Detect hand landmarks
        landmarks = self.hand_tracker.process_frame(frame)
        if not landmarks:
            self._handle_no_hand()
            return False, None
        
        # Draw hand landmarks
        self.hand_tracker.draw_landmarks(frame, landmarks)
        
        # Get hand position
        h, w, _ = frame.shape
        hand_x, hand_y = self.hand_tracker.get_hand_center(landmarks, w, h)
        
        # Transform to screen coordinates
        screen_x, screen_y = self.calibration_manager.transform_point((hand_x, hand_y))
        
        # Apply smoothing
        smoothed_x, smoothed_y = self.position_smoother.add_position(screen_x, screen_y)
        
        # Move mouse
        self.mouse.position = (smoothed_x, smoothed_y)
        
        # Handle clicking
        hand_closed = self.hand_tracker.is_hand_closed(landmarks)
        self._handle_clicking(hand_closed)
        
        # Draw visual feedback
        self._draw_feedback(frame, hand_x, hand_y, hand_closed, smoothed_x, smoothed_y)
        
        return True, (smoothed_x, smoothed_y)
    
    def _handle_no_hand(self) -> None:
        """Handle case when no hand is detected"""
        if self.is_clicking:
            self.mouse.release(Button.left)
            self.is_clicking = False
        self.position_smoother.reset()
    
    def _handle_clicking(self, hand_closed: bool) -> None:
        """Handle mouse clicking based on hand gesture"""
        if hand_closed and not self.is_clicking:
            self.mouse.press(Button.left)
            self.is_clicking = True
        elif not hand_closed and self.is_clicking:
            self.mouse.release(Button.left)
            self.is_clicking = False
    
    def _draw_feedback(self, frame, hand_x: int, hand_y: int, hand_closed: bool, 
                      screen_x: int, screen_y: int) -> None:
        """Draw visual feedback on frame"""
        import cv2
        
        # Draw hand position
        color = (0, 0, 255) if hand_closed else (0, 255, 0)
        cv2.circle(frame, (hand_x, hand_y), 15, color, -1)
        
        # Draw status text
        status = "CLICKING" if hand_closed else "MOVING"
        cv2.putText(frame, status, (hand_x + 20, hand_y - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Show screen coordinates
        cv2.putText(frame, f"Screen: {screen_x},{screen_y}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.is_clicking and self.mouse:
            self.mouse.release(Button.left)
            self.is_clicking = False
        
        self.hand_tracker.close()
        self.position_smoother.reset()


class CalibrationController:
    """Handles calibration process using hand tracking"""
    
    def __init__(self, calibration_manager: CalibrationManager):
        self.calibration_manager = calibration_manager
        self.hand_tracker = HandTracker()
        self.current_corner = 0
        self.stable_count = 0
        self.last_pos = None
        
    def initialize(self) -> None:
        """Initialize calibration controller"""
        self.hand_tracker.initialize()
        self.reset()
    
    def reset(self) -> None:
        """Reset calibration state"""
        self.current_corner = 0
        self.stable_count = 0
        self.last_pos = None
        self.calibration_manager.clear_calibration_points()
    
    def process_frame(self, frame) -> Tuple[bool, str]:
        """
        Process frame for calibration
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (calibration_complete, instruction_text)
        """
        import cv2
        from config import CALIBRATION, HAND_TRACKING
        
        if self.current_corner >= 4:
            return True, "Calibration complete!"
        
        h, w, _ = frame.shape
        corner_name = CALIBRATION['corner_names'][self.current_corner]
        
        # Draw instructions
        cv2.putText(frame, f"Place hand at: {corner_name}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Corner {self.current_corner + 1}/4", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Hold still for 3 seconds", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Detect hand landmarks
        landmarks = self.hand_tracker.process_frame(frame)
        if not landmarks:
            self.stable_count = 0
            self.last_pos = None
            return False, f"Place hand at: {corner_name}"
        
        # Draw hand landmarks
        self.hand_tracker.draw_landmarks(frame, landmarks)
        
        # Get hand center
        hand_x, hand_y = self.hand_tracker.get_hand_center(landmarks, w, h)
        cv2.circle(frame, (hand_x, hand_y), 15, (0, 0, 255), -1)
        
        # Check stability
        current_pos = (hand_x, hand_y)
        if self.hand_tracker.is_position_stable(current_pos, self.last_pos):
            self.stable_count += 1
            
            # Show countdown
            countdown = 3 - (self.stable_count // 10)
            if countdown > 0:
                cv2.putText(frame, str(countdown), (hand_x + 30, hand_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
            
            if self.stable_count >= HAND_TRACKING['stability_frames']:
                # Capture this corner
                self.calibration_manager.add_calibration_point([hand_x, hand_y])
                self.current_corner += 1
                self.stable_count = 0
                self.last_pos = None
                print(f"Captured corner {self.current_corner}: ({hand_x}, {hand_y})")
                
                if self.current_corner >= 4:
                    return True, "Calibration complete!"
        else:
            self.stable_count = 0
            self.last_pos = current_pos
        
        return False, f"Place hand at: {corner_name} (Hold still)"
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.hand_tracker.close()
