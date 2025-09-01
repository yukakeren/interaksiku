# Main application controller - refactored version
import tkinter as tk
from tkinter import messagebox
import threading
import time
import cv2
from typing import List, Tuple, Optional

# Import our modular components
from config import CAMERA_SETTINGS
from camera_manager import CameraManager
from hand_tracker import HandTracker, PositionSmoother
from calibration_manager import CalibrationManager, ManualCalibration
from mouse_controller import MouseController, CalibrationController
from ui_manager import UIManager
from video_manager import VideoDisplayManager, CameraThread, FrameProcessor, ManualCalibrationCameraFeed

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    print("Warning: pyautogui not available")
    PYAUTOGUI_AVAILABLE = False


class UltimateComfisMouseApp:
    """Main application controller - refactored version"""
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        
        # Core managers
        self.camera_manager = CameraManager()
        self.video_display = VideoDisplayManager()
        self.camera_thread = CameraThread(self.camera_manager, self.video_display)
        
        # Manual calibration camera feed
        self.manual_camera_feed = None
        
        # Get screen size
        if PYAUTOGUI_AVAILABLE:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = 1920, 1080  # Default fallback
        
        # Calibration and control
        self.calibration_manager = CalibrationManager(self.screen_w, self.screen_h)
        self.mouse_controller = MouseController(self.calibration_manager)
        self.calibration_controller = CalibrationController(self.calibration_manager)
        
        # UI
        self.ui_manager = UIManager(self.root, self)
        
        # State
        self.available_cameras: List[Tuple[int, str]] = []
        self.manual_calibration = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the application"""
        # Setup UI
        self.ui_manager.setup_main_window()
        
        # Try to load existing calibration
        if self.calibration_manager.load_calibration():
            self.ui_manager.update_calibration_status(True)
            self.ui_manager.update_status("✅ Calibration loaded successfully")
        
        # Detect cameras after UI is ready
        self.root.after(100, self.detect_cameras)
    
    def detect_cameras(self) -> None:
        """Detect available cameras"""
        self.ui_manager.update_status("🔍 Detecting cameras...")
        
        def detect_in_thread():
            cameras = self.camera_manager.detect_cameras(CAMERA_SETTINGS['max_camera_check'])
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_camera_list(cameras))
        
        threading.Thread(target=detect_in_thread, daemon=True).start()
    
    def _update_camera_list(self, cameras: List[Tuple[int, str]]) -> None:
        """Update camera list in UI"""
        self.available_cameras = cameras
        
        if cameras:
            camera_names = [name for _, name in cameras]
            self.ui_manager.camera_combo['values'] = camera_names
            if not self.ui_manager.camera_var.get():
                self.ui_manager.camera_combo.current(0)
            self.ui_manager.update_status(f"✅ Found {len(cameras)} cameras")
        else:
            self.ui_manager.camera_combo['values'] = []
            self.ui_manager.update_status("❌ No cameras found!")
            messagebox.showerror("Error", "No cameras detected! Please connect a camera and try again.")
    
    def get_selected_camera_index(self) -> int:
        """Get currently selected camera index"""
        try:
            if self.available_cameras:
                selected_idx = self.ui_manager.camera_combo.current()
                if 0 <= selected_idx < len(self.available_cameras):
                    return self.available_cameras[selected_idx][0]
            return 0
        except:
            return 0
    
    def update_calibration_mode(self) -> None:
        """Update calibration display when mode changes"""
        if self.ui_manager.current_mode == "calibration":
            # Stop any running camera
            self.stop_camera()
            
            # Update UI based on calibration method
            method = self.ui_manager.calibration_method.get()
            
            if hasattr(self.ui_manager, 'video_container'):
                # Hide both frames first
                if hasattr(self.ui_manager, 'manual_frame'):
                    self.ui_manager.manual_frame.pack_forget()
                if hasattr(self.ui_manager, 'video_frame'):
                    self.ui_manager.video_frame.pack_forget()
                
                # Show appropriate frame
                if method == "manual":
                    if hasattr(self.ui_manager, 'manual_frame'):
                        self.ui_manager.manual_frame.pack(fill="both", expand=True)
                        if hasattr(self.ui_manager, 'manual_canvas'):
                            # Refresh manual canvas
                            self.ui_manager.manual_canvas._draw_points()
                            
                            # Start camera background if camera is selected
                            if self.ui_manager.camera_var.get():
                                camera_index = self.get_selected_camera_index()
                                use_flip = self.ui_manager.use_flip.get()
                                
                                self.manual_camera_feed = ManualCalibrationCameraFeed(
                                    self.camera_manager,
                                    self.ui_manager.manual_canvas
                                )
                                
                                if self.manual_camera_feed.start(camera_index, use_flip):
                                    print("Started camera background for manual calibration")
                else:
                    if hasattr(self.ui_manager, 'video_frame'):
                        self.ui_manager.video_frame.pack(fill="both", expand=True)
                        # Add placeholder
                        self.video_display.clear_display(
                            self.ui_manager.video_frame,
                            "📹 Camera feed will appear here\nClick 'Start Calibration' to begin"
                        )
    
    def start_calibration(self) -> None:
        """Start calibration process"""
        if not self.ui_manager.camera_var.get():
            messagebox.showerror("Error", "Please select a camera first!")
            return
        
        camera_index = self.get_selected_camera_index()
        method = self.ui_manager.calibration_method.get()
        
        # Update UI
        if hasattr(self.ui_manager, 'start_cal_btn'):
            self.ui_manager.start_cal_btn.config(state="disabled")
        if hasattr(self.ui_manager, 'save_cal_btn'):
            self.ui_manager.save_cal_btn.config(state="disabled")
        
        if method == "manual":
            self._start_manual_calibration()
        else:
            self._start_opencv_calibration(camera_index)
    
    def _start_manual_calibration(self) -> None:
        """Start manual calibration"""
        # Get points from manual canvas
        if hasattr(self.ui_manager, 'manual_canvas') and self.ui_manager.manual_canvas:
            points = self.ui_manager.manual_canvas.manual_calibration.get_points()
            self.calibration_manager.set_calibration_points(points)
            
            # Start camera feed for background
            camera_index = self.get_selected_camera_index()
            use_flip = self.ui_manager.use_flip.get()
            
            # Initialize manual camera feed
            self.manual_camera_feed = ManualCalibrationCameraFeed(
                self.camera_manager, 
                self.ui_manager.manual_canvas
            )
            
            if self.manual_camera_feed.start(camera_index, use_flip):
                print("Manual camera background started successfully")
            else:
                print("Failed to start manual camera background")
            
            if hasattr(self.ui_manager, 'save_cal_btn'):
                self.ui_manager.save_cal_btn.config(state="normal")
            if hasattr(self.ui_manager, 'start_cal_btn'):
                self.ui_manager.start_cal_btn.config(state="normal")
            if hasattr(self.ui_manager, 'cal_instruction_label'):
                self.ui_manager.cal_instruction_label.config(
                    text="✅ Manual calibration ready with camera background. Drag points to adjust. Click 'Save Calibration' to finish."
                )
    
    def _start_opencv_calibration(self, camera_index: int) -> None:
        """Start OpenCV calibration"""
        self.calibration_controller.initialize()
        
        if hasattr(self.ui_manager, 'cal_instruction_label'):
            self.ui_manager.cal_instruction_label.config(text="🎥 Starting camera... Please wait...")
        
        # Start camera thread
        success = self.camera_thread.start(
            camera_index,
            self._opencv_calibration_loop
        )
        
        if not success:
            messagebox.showerror("Error", "Failed to open camera!")
            if hasattr(self.ui_manager, 'start_cal_btn'):
                self.ui_manager.start_cal_btn.config(state="normal")
            if hasattr(self.ui_manager, 'cal_instruction_label'):
                self.ui_manager.cal_instruction_label.config(
                    text="❌ Failed to open camera. Try different camera."
                )
    
    def _opencv_calibration_loop(self, cap) -> None:
        """OpenCV calibration loop"""
        frame_count = 0
        
        # Update status
        self.root.after(0, lambda: self.ui_manager.cal_instruction_label.config(
            text="✋ Place your hand at the specified corner and hold still..."
        ))
        
        while self.camera_thread.is_running():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Preprocess frame
            if self.ui_manager.use_flip.get():
                frame = cv2.flip(frame, 1)
            
            # Process frame for calibration
            calibration_complete, instruction = self.calibration_controller.process_frame(frame)
            
            # Update instruction in main thread
            if frame_count % 30 == 0:  # Update every 30 frames
                self.root.after(0, lambda msg=instruction: 
                    self.ui_manager.cal_instruction_label.config(text=msg))
            
            # Display frame
            if hasattr(self.ui_manager, 'video_frame'):
                self.video_display.display_frame(
                    frame,
                    self.ui_manager.video_frame,
                    self.camera_thread.is_running
                )
            
            # Check if calibration is complete
            if calibration_complete:
                self.root.after(0, self._on_calibration_complete)
                break
            
            time.sleep(0.033)  # ~30 FPS
        
        # Cleanup
        self.calibration_controller.cleanup()
        self.root.after(0, lambda: self.ui_manager.start_cal_btn.config(state="normal"))
    
    def _on_calibration_complete(self) -> None:
        """Handle calibration completion"""
        if hasattr(self.ui_manager, 'save_cal_btn'):
            self.ui_manager.save_cal_btn.config(state="normal")
        if hasattr(self.ui_manager, 'cal_instruction_label'):
            self.ui_manager.cal_instruction_label.config(
                text="✅ Calibration complete! Click 'Save Calibration' to finish."
            )
    
    def save_calibration(self) -> None:
        """Save calibration data"""
        if not self.calibration_manager.is_calibrated():
            messagebox.showerror("Error", "No calibration data to save!")
            return
        
        method = self.ui_manager.calibration_method.get()
        flip_setting = self.ui_manager.use_flip.get()
        
        success = self.calibration_manager.save_calibration(method, flip_setting)
        
        if success:
            self.ui_manager.update_calibration_status(True)
            self.ui_manager.update_status("✅ Calibration saved successfully!")
            messagebox.showinfo("Success", "Calibration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save calibration!")
    
    def start_mouse_control(self) -> None:
        """Start mouse control"""
        if not self.calibration_manager.is_calibrated():
            messagebox.showerror("Error", "Please complete calibration first!")
            return
        
        if not self.ui_manager.camera_var.get():
            messagebox.showerror("Error", "Please select a camera first!")
            return
        
        camera_index = self.get_selected_camera_index()
        
        # Initialize mouse controller
        try:
            if not self.mouse_controller.initialize():
                messagebox.showerror("Mouse Control Error", 
                    "Failed to initialize mouse controller. Hand tracking may not be available.")
                return
        except Exception as e:
            messagebox.showerror("Mouse Control Error", 
                f"Failed to initialize mouse controller: {str(e)}\n\n"
                "This might be due to missing dependencies in the standalone version.")
            return
        
        # Update UI
        if hasattr(self.ui_manager, 'start_mouse_btn'):
            self.ui_manager.start_mouse_btn.config(state="disabled")
        if hasattr(self.ui_manager, 'mouse_status_label'):
            self.ui_manager.mouse_status_label.config(text="🎥 Starting camera... Please wait...")
        
        # Start camera thread
        success = self.camera_thread.start(
            camera_index,
            self._mouse_control_loop
        )
        
        if not success:
            messagebox.showerror("Error", "Failed to open camera!")
            if hasattr(self.ui_manager, 'start_mouse_btn'):
                self.ui_manager.start_mouse_btn.config(state="normal")
            if hasattr(self.ui_manager, 'mouse_status_label'):
                self.ui_manager.mouse_status_label.config(
                    text="❌ Failed to open camera. Try different camera."
                )
    
    def _mouse_control_loop(self, cap) -> None:
        """Mouse control loop"""
        # Update status
        self.root.after(0, lambda: self.ui_manager.mouse_status_label.config(
            text="✅ Mouse control active! Move your hand to control cursor."
        ))
        
        while self.camera_thread.is_running():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Preprocess frame
            if self.ui_manager.use_flip.get():
                frame = cv2.flip(frame, 1)
            
            # Draw calibration area
            self.calibration_manager.draw_calibration_area(frame)
            
            # Process frame for mouse control
            smoothing_factor = self.ui_manager.smoothing.get()
            hand_detected, screen_pos = self.mouse_controller.process_frame(frame, smoothing_factor)
            
            # Display frame
            if hasattr(self.ui_manager, 'mouse_video_frame') and self.ui_manager.mouse_video_frame:
                self.video_display.display_frame(
                    frame,
                    self.ui_manager.mouse_video_frame,
                    self.camera_thread.is_running
                )
            
            # Small delay to control frame rate
            time.sleep(0.033)  # ~30 FPS
        
        # Update status when loop ends
        self.root.after(0, lambda: self.ui_manager.mouse_status_label.config(
            text="Mouse control stopped."
        ))
        
        # Cleanup
        self.mouse_controller.cleanup()
        self.root.after(0, lambda: self.ui_manager.start_mouse_btn.config(state="normal"))
        self.root.after(0, lambda: self.ui_manager.mouse_status_label.config(
            text="Mouse control stopped."
        ))
    
    def stop_camera(self) -> None:
        """Stop camera operations"""
        self.camera_thread.stop()
        
        # Stop manual camera feed if running
        if self.manual_camera_feed:
            self.manual_camera_feed.stop()
            self.manual_camera_feed = None
        
        # Clear video displays
        if hasattr(self.ui_manager, 'video_frame'):
            self.video_display.clear_display(self.ui_manager.video_frame)
        if hasattr(self.ui_manager, 'mouse_video_frame'):
            self.video_display.clear_display(self.ui_manager.mouse_video_frame)
        
        # Update UI buttons
        self._update_ui_after_stop()
    
    def _update_ui_after_stop(self) -> None:
        """Update UI after stopping camera"""
        try:
            if (hasattr(self.ui_manager, 'start_cal_btn') and 
                self.ui_manager.start_cal_btn and 
                self.ui_manager.start_cal_btn.winfo_exists()):
                self.ui_manager.start_cal_btn.config(state="normal")
        except (tk.TclError, AttributeError):
            pass
        
        try:
            if (hasattr(self.ui_manager, 'start_mouse_btn') and 
                self.ui_manager.start_mouse_btn and 
                self.ui_manager.start_mouse_btn.winfo_exists()):
                self.ui_manager.start_mouse_btn.config(state="normal")
        except (tk.TclError, AttributeError):
            pass
    
    def update_manual_calibration_points(self, points: List[List[int]]) -> None:
        """Update manual calibration points"""
        self.calibration_manager.set_calibration_points(points)
        
        if hasattr(self.ui_manager, 'save_cal_btn'):
            self.ui_manager.save_cal_btn.config(state="normal")
    
    def is_calibrated(self) -> bool:
        """Check if system is calibrated"""
        return self.calibration_manager.is_calibrated()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size"""
        return self.screen_w, self.screen_h
    
    def run(self) -> None:
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self) -> None:
        """Handle application closing"""
        try:
            self.stop_camera()
        except:
            pass
        
        try:
            if self.manual_camera_feed:
                self.manual_camera_feed.stop()
        except:
            pass
        
        try:
            self.root.destroy()
        except:
            pass


def main():
    """Main entry point"""
    app = UltimateComfisMouseApp()
    app.run()


if __name__ == "__main__":
    main()
