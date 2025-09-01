# Video display utilities
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time
from typing import Optional, Callable
from config import COLORS


class VideoDisplayManager:
    """Manages video display in tkinter frames"""
    
    def __init__(self):
        self.current_photo = None
        
    def display_frame(self, frame, target_frame: tk.Widget, running_flag: Callable[[], bool]) -> None:
        """
        Display OpenCV frame in tkinter widget
        
        Args:
            frame: OpenCV frame
            target_frame: Target tkinter widget
            running_flag: Function that returns True if video should continue
        """
        if not running_flag():
            return
        
        try:
            # Resize frame to fit display
            display_frame = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update display in main thread
            def update_display():
                try:
                    if not running_flag() or not target_frame.winfo_exists():
                        return
                    
                    # Clear existing video labels
                    for widget in target_frame.winfo_children():
                        if isinstance(widget, tk.Label) and hasattr(widget, 'image'):
                            widget.destroy()
                    
                    # Create new video label
                    video_label = tk.Label(target_frame, image=imgtk, bg=COLORS['black'])
                    video_label.image = imgtk  # Keep reference
                    video_label.pack(expand=True, fill="both")
                    
                    # Store reference to prevent garbage collection
                    self.current_photo = imgtk
                    
                except Exception as e:
                    print(f"Update display error: {e}")
            
            # Schedule update in main thread
            if target_frame.winfo_exists():
                target_frame.after(0, update_display)
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def clear_display(self, target_frame: tk.Widget, placeholder_text: str = "") -> None:
        """
        Clear video display and optionally show placeholder
        
        Args:
            target_frame: Target tkinter widget
            placeholder_text: Optional placeholder text
        """
        try:
            if not target_frame or not target_frame.winfo_exists():
                return
            
            # Clear all video labels
            for widget in target_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.destroy()
            
            # Add placeholder if specified
            if placeholder_text:
                placeholder_label = tk.Label(
                    target_frame,
                    text=placeholder_text,
                    font=("Arial", 12),
                    fg=COLORS['white'],
                    bg=COLORS['black']
                )
                placeholder_label.pack(expand=True)
            
        except Exception as e:
            print(f"Clear display error: {e}")


class CameraThread:
    """Manages camera operations in separate thread"""
    
    def __init__(self, camera_manager, video_display_manager):
        self.camera_manager = camera_manager
        self.video_display = video_display_manager
        self.running = False
        self.thread = None
        self.cap = None
        
    def start(self, camera_index: int, loop_function: Callable, *args) -> bool:
        """
        Start camera thread
        
        Args:
            camera_index: Camera index to use
            loop_function: Function to run in thread
            *args: Arguments for loop function
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.stop()
        
        # Initialize camera
        self.cap = self.camera_manager.initialize_camera(camera_index)
        if not self.cap:
            return False
        
        self.running = True
        self.thread = threading.Thread(
            target=loop_function,
            args=(self.cap, *args),
            daemon=True
        )
        self.thread.start()
        
        return True
    
    def stop(self) -> None:
        """Stop camera thread"""
        self.running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
    
    def is_running(self) -> bool:
        """Check if camera thread is running"""
        return self.running


class FrameProcessor:
    """Base class for frame processing"""
    
    def __init__(self, use_flip: bool = False):
        self.use_flip = use_flip
    
    def preprocess_frame(self, frame):
        """Preprocess frame (flip if needed)"""
        if self.use_flip:
            frame = cv2.flip(frame, 1)
        return frame
    
    def process_frame(self, frame):
        """Process frame - to be implemented by subclasses"""
        raise NotImplementedError
    
    def set_flip(self, use_flip: bool) -> None:
        """Update flip setting"""
        self.use_flip = use_flip


class ManualCalibrationCameraFeed:
    """Manages camera feed for manual calibration background"""
    
    def __init__(self, camera_manager, canvas_widget):
        self.camera_manager = camera_manager
        self.canvas_widget = canvas_widget
        self.cap = None
        self.running = False
        self.use_flip = False
        
    def start(self, camera_index: int, use_flip: bool = False) -> bool:
        """
        Start camera feed for manual calibration
        
        Args:
            camera_index: Camera index to use
            use_flip: Whether to flip the camera feed
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.stop()
        
        self.use_flip = use_flip
        self.cap = self.camera_manager.initialize_camera(camera_index)
        
        if not self.cap:
            return False
        
        self.running = True
        self._update_background()
        
        return True
    
    def stop(self) -> None:
        """Stop camera feed"""
        self.running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear background from canvas
        if hasattr(self.canvas_widget, 'clear_camera_background'):
            self.canvas_widget.clear_camera_background()
    
    def _update_background(self) -> None:
        """Update camera background"""
        if not self.running or not self.cap:
            return
        
        try:
            ret, frame = self.cap.read()
            if ret:
                # Apply flip if needed
                if self.use_flip:
                    import cv2
                    frame = cv2.flip(frame, 1)
                
                # Update canvas background
                if hasattr(self.canvas_widget, 'update_camera_background'):
                    self.canvas_widget.update_camera_background(frame)
                
                # Schedule next update
                if self.running and hasattr(self.canvas_widget, 'canvas') and self.canvas_widget.canvas:
                    try:
                        self.canvas_widget.canvas.after(33, self._update_background)  # ~30 FPS
                    except:
                        pass  # Canvas might be destroyed
        except Exception as e:
            print(f"Manual camera background error: {e}")
            if self.running:
                try:
                    if hasattr(self.canvas_widget, 'canvas') and self.canvas_widget.canvas:
                        self.canvas_widget.canvas.after(100, self._update_background)  # Retry with longer delay
                except:
                    pass
