import cv2
import mediapipe as mp
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading
import time
from pynput.mouse import Controller, Button
import pyautogui
import math

# Set environment variables for Windows compatibility
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

class UltimateComfisMouse:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ultimate Comfis Mouse - Calibration & Control")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Variables
        self.mouse = Controller()
        self.screen_w, self.screen_h = pyautogui.size()
        self.selected_camera = 0
        self.camera_indices = []  # Store actual camera indices
        self.use_flip = tk.BooleanVar(value=False)
        self.calibration_method = tk.StringVar(value="opencv")
        self.smoothing = tk.IntVar(value=5)
        self.cap = None
        self.running = False
        self.current_mode = "home"
        
        # Calibration variables
        self.calibration_points = []
        self.corner_names = ["Top Left", "Top Right", "Bottom Right", "Bottom Left"]
        self.current_corner = 0
        self.calibration_matrix = None
        
        # GUI variables for manual calibration
        self.canvas_width = 640
        self.canvas_height = 480
        self.manual_points = [[100, 100], [540, 100], [540, 380], [100, 380]]
        self.dragging = False
        self.selected_point = -1
        self.point_radius = 12
        
        # Mouse control variables
        self.is_clicking = False
        self.prev_positions_x = []
        self.prev_positions_y = []
        
        # MediaPipe initialization
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = None
        
        # Setup UI
        self.setup_ui()
        
        # Try to load calibration if it exists
        self.try_load_calibration()
        
        # Detect cameras on startup
        self.root.after(100, self.detect_cameras)
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🖱️ ULTIMATE COMFIS MOUSE", 
                              font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(header_frame, text="All-in-One Hand Tracking Calibration & Mouse Control", 
                                 font=("Arial", 12), fg="#ecf0f1", bg="#2c3e50")
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg="#f0f0f0", width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Mode selection
        mode_frame = tk.LabelFrame(left_panel, text="🎯 Mode Selection", font=("Arial", 12, "bold"), bg="#f0f0f0")
        mode_frame.pack(fill="x", pady=(0, 15))
        
        self.home_btn = tk.Button(mode_frame, text="🏠 Home", command=lambda: self.switch_mode("home"), 
                                 font=("Arial", 11), width=25, height=2, bg="#3498db", fg="white")
        self.home_btn.pack(pady=5, padx=10)
        
        self.calibrate_btn = tk.Button(mode_frame, text="📐 Calibration", command=lambda: self.switch_mode("calibration"), 
                                      font=("Arial", 11), width=25, height=2, bg="#e74c3c", fg="white")
        self.calibrate_btn.pack(pady=5, padx=10)
        
        self.mouse_btn = tk.Button(mode_frame, text="🖱️ Mouse Control", command=lambda: self.switch_mode("mouse_control"), 
                                  font=("Arial", 11), width=25, height=2, bg="#27ae60", fg="white")
        self.mouse_btn.pack(pady=5, padx=10)
        
        # Settings
        settings_frame = tk.LabelFrame(left_panel, text="⚙️ Settings", font=("Arial", 12, "bold"), bg="#f0f0f0")
        settings_frame.pack(fill="x", pady=(0, 15))
        
        # Camera selection
        tk.Label(settings_frame, text="📷 Camera:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=(10, 5))
        
        camera_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        camera_frame.pack(fill="x", padx=10)
        
        self.camera_var = tk.StringVar()
        self.camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var, state="readonly", width=20)
        self.camera_combo.pack(side="left", fill="x", expand=True)
        
        detect_btn = tk.Button(camera_frame, text="🔍", command=self.detect_cameras, font=("Arial", 9), width=3)
        detect_btn.pack(side="right", padx=(5, 0))
        
        # Flip option
        tk.Label(settings_frame, text="🔄 Display:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=(15, 5))
        flip_checkbox = tk.Checkbutton(settings_frame, text="Mirror/Flip horizontal", 
                                      variable=self.use_flip, font=("Arial", 10), bg="#f0f0f0")
        flip_checkbox.pack(anchor="w", padx=20)
        
        # Calibration method
        tk.Label(settings_frame, text="📏 Calibration Method:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=(15, 5))
        
        method_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        method_frame.pack(fill="x", padx=20)
        
        tk.Radiobutton(method_frame, text="Manual (Drag & Drop)", variable=self.calibration_method, 
                      value="manual", font=("Arial", 9), bg="#f0f0f0", 
                      command=self.update_calibration_mode).pack(anchor="w")
        tk.Radiobutton(method_frame, text="OpenCV Hand Tracking", variable=self.calibration_method, 
                      value="opencv", font=("Arial", 9), bg="#f0f0f0",
                      command=self.update_calibration_mode).pack(anchor="w")
        
        # Smoothing
        tk.Label(settings_frame, text="🎯 Mouse Smoothing:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=(15, 5))
        
        smoothing_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        smoothing_frame.pack(fill="x", padx=20)
        
        tk.Scale(smoothing_frame, from_=1, to=10, orient="horizontal", variable=self.smoothing, 
                length=200, bg="#f0f0f0").pack()
        tk.Label(smoothing_frame, text="1=Fast, 10=Smooth", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack()
        
        # Calibration status
        self.cal_status_frame = tk.LabelFrame(left_panel, text="📊 Calibration Status", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.cal_status_frame.pack(fill="x", pady=(0, 15))
        
        self.cal_status_label = tk.Label(self.cal_status_frame, text="❌ Not Calibrated", 
                                        font=("Arial", 10), fg="red", bg="#f0f0f0")
        self.cal_status_label.pack(pady=10)
        
        # Right panel - Video/Content
        self.right_panel = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 10), 
                                   bd=1, relief="sunken", anchor="w", bg="#ecf0f1")
        self.status_label.pack(fill="x", side="bottom")
        
        # Show home content by default
        self.show_home_content()
        self.update_mode_buttons()
        
    def detect_cameras(self):
        self.status_label.config(text="🔍 Detecting cameras...")
        self.root.update()
        
        available_cameras = []
        
        for i in range(10):  # Check first 10 camera indices
            try:
                print(f"Testing camera {i}...")
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Try to get camera name
                        camera_name = f"Camera {i}"
                        try:
                            # Try to get DirectShow device name
                            backend_name = cap.getBackendName()
                            if backend_name == "DSHOW":
                                camera_name = f"Camera {i} (DirectShow)"
                            else:
                                camera_name = f"Camera {i} ({backend_name})"
                        except:
                            camera_name = f"Camera {i}"
                        
                        available_cameras.append((i, camera_name))
                        print(f"✅ {camera_name}: Available")
                    cap.release()
                else:
                    # Try without DirectShow
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            camera_name = f"Camera {i} (Standard)"
                            available_cameras.append((i, camera_name))
                            print(f"✅ {camera_name}: Available")
                        cap.release()
            except Exception as e:
                print(f"❌ Camera {i}: Error - {e}")
                continue
        
        if available_cameras:
            camera_names = [name for _, name in available_cameras]
            self.camera_indices = [idx for idx, _ in available_cameras]
            self.camera_combo['values'] = camera_names
            if not self.camera_var.get():
                self.camera_combo.current(0)
            self.status_label.config(text=f"✅ Found {len(available_cameras)} cameras")
            print(f"Found cameras: {camera_names}")
        else:
            self.camera_combo['values'] = []
            self.camera_indices = []
            self.status_label.config(text="❌ No cameras found!")
            messagebox.showerror("Error", "No cameras detected! Please connect a camera and try again.")
    
    def get_camera_index(self):
        """Extract camera index from combo selection"""
        try:
            if hasattr(self, 'camera_indices') and self.camera_indices:
                selected_idx = self.camera_combo.current()
                if 0 <= selected_idx < len(self.camera_indices):
                    return self.camera_indices[selected_idx]
            
            # Fallback: extract from text
            camera_text = self.camera_var.get()
            if camera_text:
                try:
                    return int(camera_text.split()[1])
                except:
                    return 0
            return 0
        except:
            return 0
    
    def switch_mode(self, mode):
        if self.running:
            self.stop_camera()
        
        self.current_mode = mode
        self.update_mode_buttons()
        
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        if mode == "home":
            self.show_home_content()
        elif mode == "calibration":
            self.show_calibration_content()
        elif mode == "mouse_control":
            self.show_mouse_control_content()
    
    def update_mode_buttons(self):
        # Reset all buttons
        self.home_btn.config(bg="#3498db" if self.current_mode != "home" else "#2980b9")
        self.calibrate_btn.config(bg="#e74c3c" if self.current_mode != "calibration" else "#c0392b")
        self.mouse_btn.config(bg="#27ae60" if self.current_mode != "mouse_control" else "#229954")
    
    def show_home_content(self):
        # Welcome content
        welcome_frame = tk.Frame(self.right_panel, bg="white")
        welcome_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(welcome_frame, text="🎉 Welcome to Ultimate Comfis Mouse!", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=(0, 20))
        
        # Description
        desc_text = """
This application combines calibration and mouse control into one easy-to-use interface.

🔹 CALIBRATION: Set up your camera and define the tracking area
🔹 MOUSE CONTROL: Use hand gestures to control your mouse cursor

Follow these steps:
"""
        tk.Label(welcome_frame, text=desc_text, font=("Arial", 12), bg="white", justify="left").pack(pady=(0, 20))
        
        # Steps
        steps_frame = tk.Frame(welcome_frame, bg="white")
        steps_frame.pack(fill="x")
        
        steps = [
            ("1️⃣", "Select your camera from the dropdown"),
            ("2️⃣", "Go to Calibration mode and set up tracking area"),
            ("3️⃣", "Switch to Mouse Control mode to start using"),
        ]
        
        for emoji, step in steps:
            step_frame = tk.Frame(steps_frame, bg="white")
            step_frame.pack(fill="x", pady=5)
            tk.Label(step_frame, text=emoji, font=("Arial", 14), bg="white").pack(side="left", padx=(0, 10))
            tk.Label(step_frame, text=step, font=("Arial", 11), bg="white").pack(side="left")
        
        # System info
        info_frame = tk.LabelFrame(welcome_frame, text="📊 System Information", bg="white", font=("Arial", 11, "bold"))
        info_frame.pack(fill="x", pady=(30, 0))
        
        info_text = f"""
Screen Resolution: {self.screen_w} x {self.screen_h}
MediaPipe: ✅ Available
OpenCV: ✅ Available
        """
        tk.Label(info_frame, text=info_text, font=("Arial", 10), bg="white", justify="left").pack(padx=10, pady=10)
    
    def show_calibration_content(self):
        cal_frame = tk.Frame(self.right_panel, bg="white")
        cal_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(cal_frame, text="📐 Camera Calibration", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 10))
        
        # Instructions
        if self.calibration_method.get() == "manual":
            instruction_text = "🖱️ MANUAL MODE: Drag the colored points to the corners of your tracking area"
        else:
            instruction_text = "✋ OPENCV MODE: Follow the on-screen instructions to place your hand at each corner"
        
        tk.Label(cal_frame, text=instruction_text, font=("Arial", 11), bg="white", fg="blue").pack(pady=(0, 15))
        
        # Control buttons
        control_frame = tk.Frame(cal_frame, bg="white")
        control_frame.pack(fill="x", pady=(0, 15))
        
        self.start_cal_btn = tk.Button(control_frame, text="▶️ Start Calibration", 
                                      command=self.start_calibration, font=("Arial", 11), 
                                      bg="#27ae60", fg="white", width=20)
        self.start_cal_btn.pack(side="left", padx=(0, 10))
        
        self.save_cal_btn = tk.Button(control_frame, text="💾 Save Calibration", 
                                     command=self.save_calibration, font=("Arial", 11), 
                                     bg="#3498db", fg="white", width=20, state="disabled")
        self.save_cal_btn.pack(side="left", padx=(0, 10))
        
        self.stop_cal_btn = tk.Button(control_frame, text="⏹️ Stop", 
                                     command=self.stop_camera, font=("Arial", 11), 
                                     bg="#e74c3c", fg="white", width=15)
        self.stop_cal_btn.pack(side="left")
        
        # Video/Canvas frame container
        self.video_container = tk.Frame(cal_frame, bg="white")
        self.video_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create video frame for camera display (OpenCV mode)
        self.video_frame = tk.Frame(self.video_container, bg="black", relief="solid", bd=2)
        
        # Create manual canvas frame (Manual mode) 
        self.manual_frame = tk.Frame(self.video_container, bg="white", relief="solid", bd=2)
        
        # Show appropriate frame based on calibration method
        if self.calibration_method.get() == "manual":
            self.manual_frame.pack(fill="both", expand=True)
            self.setup_manual_calibration_canvas()
        else:
            self.video_frame.pack(fill="both", expand=True)
            # Add placeholder for camera
            placeholder_label = tk.Label(self.video_frame, text="📹 Camera feed will appear here\nClick 'Start Calibration' to begin", 
                                        font=("Arial", 12), fg="white", bg="black")
            placeholder_label.pack(expand=True)
        
        # Status
        self.cal_instruction_label = tk.Label(cal_frame, text="Select camera and click 'Start Calibration'", 
                                             font=("Arial", 10), bg="white", fg="gray")
        self.cal_instruction_label.pack()
    
    def setup_manual_calibration_canvas(self):
        self.manual_canvas = tk.Canvas(self.manual_frame, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.manual_canvas.pack(expand=True)
        
        # Bind events
        self.manual_canvas.bind("<Button-1>", self.on_canvas_click)
        self.manual_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.manual_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.draw_manual_points()
    
    def draw_manual_points(self):
        # Don't delete background image - only delete points and overlays
        self.manual_canvas.delete("points")
        self.manual_canvas.delete("grid")
        self.manual_canvas.delete("overlay")
        
        # Draw background grid (only if no camera background)
        if not hasattr(self, 'manual_bg_photo'):
            for i in range(0, self.canvas_width, 50):
                self.manual_canvas.create_line(i, 0, i, self.canvas_height, fill="#d0d0d0", width=1, tags="grid")
            for i in range(0, self.canvas_height, 50):
                self.manual_canvas.create_line(0, i, self.canvas_width, i, fill="#d0d0d0", width=1, tags="grid")
        
        # Draw calibration area
        if len(self.manual_points) == 4:
            points = []
            for point in self.manual_points:
                points.extend(point)
            self.manual_canvas.create_polygon(points, outline="yellow", width=3, fill="", stipple="gray25", tags="overlay")
        
        # Draw points
        colors = ["red", "green", "blue", "orange"]
        for i, (point, color) in enumerate(zip(self.manual_points, colors)):
            x, y = point
            r = self.point_radius
            if self.selected_point == i:
                r += 4
            
            self.manual_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="white", width=3, tags="points")
            self.manual_canvas.create_text(x, y-r-15, text=self.corner_names[i], fill=color, font=("Arial", 9, "bold"), tags="points")
    
    def on_canvas_click(self, event):
        # Find closest point
        min_dist = float('inf')
        closest_point = -1
        
        for i, point in enumerate(self.manual_points):
            dist = math.sqrt((event.x - point[0])**2 + (event.y - point[1])**2)
            if dist < min_dist and dist <= self.point_radius + 5:
                min_dist = dist
                closest_point = i
        
        if closest_point != -1:
            self.selected_point = closest_point
            self.dragging = True
            self.draw_manual_points()
    
    def on_canvas_drag(self, event):
        if self.dragging and self.selected_point != -1:
            # Keep within bounds
            x = max(20, min(self.canvas_width - 20, event.x))
            y = max(20, min(self.canvas_height - 20, event.y))
            
            self.manual_points[self.selected_point] = [x, y]
            self.draw_manual_points()
    
    def on_canvas_release(self, event):
        self.dragging = False
        self.selected_point = -1
        self.draw_manual_points()
        
        # Enable save button if we have 4 points
        if len(self.manual_points) == 4:
            self.save_cal_btn.config(state="normal")
    
    def show_mouse_control_content(self):
        mouse_frame = tk.Frame(self.right_panel, bg="white")
        mouse_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(mouse_frame, text="🖱️ Mouse Control", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 10))
        
        # Check if calibrated
        if not self.is_calibrated():
            tk.Label(mouse_frame, text="⚠️ Please complete calibration first!", 
                    font=("Arial", 12), bg="white", fg="red").pack(pady=20)
            
            cal_btn = tk.Button(mouse_frame, text="📐 Go to Calibration", 
                              command=lambda: self.switch_mode("calibration"),
                              font=("Arial", 12), bg="#e74c3c", fg="white")
            cal_btn.pack()
            return
        
        # Instructions
        instruction_text = """
✋ Instructions:
• Move your hand in the calibrated area to control the cursor
• Make a fist to click (close your hand)
• Keep your hand visible to the camera
        """
        tk.Label(mouse_frame, text=instruction_text, font=("Arial", 11), bg="white", justify="left").pack(pady=(0, 15))
        
        # Control buttons
        control_frame = tk.Frame(mouse_frame, bg="white")
        control_frame.pack(fill="x", pady=(0, 15))
        
        self.start_mouse_btn = tk.Button(control_frame, text="▶️ Start Mouse Control", 
                                        command=self.start_mouse_control, font=("Arial", 11), 
                                        bg="#27ae60", fg="white", width=20)
        self.start_mouse_btn.pack(side="left", padx=(0, 10))
        
        self.stop_mouse_btn = tk.Button(control_frame, text="⏹️ Stop", 
                                       command=self.stop_camera, font=("Arial", 11), 
                                       bg="#e74c3c", fg="white", width=15)
        self.stop_mouse_btn.pack(side="left")
        
        # Video frame
        self.mouse_video_frame = tk.Frame(mouse_frame, bg="black", relief="solid", bd=2)
        self.mouse_video_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Status
        self.mouse_status_label = tk.Label(mouse_frame, text="Click 'Start Mouse Control' to begin", 
                                          font=("Arial", 10), bg="white", fg="gray")
        self.mouse_status_label.pack()
    
    def is_calibrated(self):
        return len(self.calibration_points) == 4 and self.calibration_matrix is not None
    
    def try_load_calibration(self):
        """Try to load existing calibration"""
        try:
            if os.path.exists("calibration_points.npy"):
                self.calibration_points = np.load("calibration_points.npy").tolist()
                
                # Check calibration method
                if os.path.exists("calibration_method.txt"):
                    with open("calibration_method.txt", "r") as f:
                        method = f.read().strip()
                        self.calibration_method.set("opencv" if method == "opencv_hand_tracking" else "manual")
                
                # Check flip setting
                if os.path.exists("calibration_flip.txt"):
                    with open("calibration_flip.txt", "r") as f:
                        flip_setting = f.read().strip()
                        self.use_flip.set(flip_setting.lower() == "true")
                
                # Set up transformation matrix
                self.setup_transformation_matrix()
                self.update_calibration_status()
                
                self.status_label.config(text="✅ Calibration loaded successfully")
                return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
        return False
    
    def setup_transformation_matrix(self):
        """Set up perspective transformation matrix from calibration points to screen"""
        if len(self.calibration_points) == 4:
            screen_corners = np.float32([[0, 0], [self.screen_w, 0], [self.screen_w, self.screen_h], [0, self.screen_h]])
            self.calibration_matrix = cv2.getPerspectiveTransform(np.float32(self.calibration_points), screen_corners)
    
    def update_calibration_mode(self):
        """Update calibration display when mode changes"""
        print(f"update_calibration_mode called - method: {self.calibration_method.get()}")
        
        if self.current_mode == "calibration" and hasattr(self, 'video_container'):
            # Hide both frames first
            if hasattr(self, 'manual_frame'):
                self.manual_frame.pack_forget()
            if hasattr(self, 'video_frame'):
                self.video_frame.pack_forget()
            
            # Show appropriate frame
            if self.calibration_method.get() == "manual":
                print("Showing manual frame with camera background")
                if hasattr(self, 'manual_frame'):
                    self.manual_frame.pack(fill="both", expand=True)
                    if hasattr(self, 'manual_canvas'):
                        self.draw_manual_points()
                    # Start camera feed for manual mode background
                    self.start_manual_camera_feed()
            else:
                print("Showing video frame")
                if hasattr(self, 'video_frame'):
                    self.video_frame.pack(fill="both", expand=True)
                # Stop manual camera feed if it was running
                if hasattr(self, 'manual_camera_running') and self.manual_camera_running:
                    self.stop_manual_camera_feed()
                    # Clear any existing widgets and add placeholder
                    for widget in self.video_frame.winfo_children():
                        widget.destroy()
                    placeholder_label = tk.Label(self.video_frame, text="📹 Camera feed will appear here\nClick 'Start Calibration' to begin", 
                                                font=("Arial", 12), fg="white", bg="black")
                    placeholder_label.pack(expand=True)
    
    def update_calibration_status(self):
        if self.is_calibrated():
            self.cal_status_label.config(text="✅ Calibrated", fg="green")
        else:
            self.cal_status_label.config(text="❌ Not Calibrated", fg="red")
    
    def start_calibration(self):
        print("start_calibration called")
        
        if not self.camera_var.get():
            print("No camera selected")
            messagebox.showerror("Error", "Please select a camera first!")
            return
        
        print(f"Starting calibration with camera: {self.camera_var.get()}")
        
        self.selected_camera = self.get_camera_index()
        print(f"Selected camera index: {self.selected_camera}")
        
        self.current_corner = 0
        self.calibration_points = []
        
        # Update UI
        self.start_cal_btn.config(state="disabled")
        self.save_cal_btn.config(state="disabled")
        
        if self.calibration_method.get() == "manual":
            print("Using manual calibration method with camera background")
            # Start camera feed for manual calibration background
            self.start_manual_camera_feed()
            # Use manual points from canvas
            self.calibration_points = self.manual_points.copy()
            self.setup_transformation_matrix()
            self.save_cal_btn.config(state="normal")
            self.start_cal_btn.config(state="normal")
            self.cal_instruction_label.config(text="✅ Manual calibration ready with camera background. Drag points to adjust. Click 'Save Calibration' to finish.")
        else:
            print("Using OpenCV calibration method")
            # Switch to video frame for OpenCV calibration
            if hasattr(self, 'manual_frame'):
                print("Hiding manual frame")
                self.manual_frame.pack_forget()
            if hasattr(self, 'video_frame'):
                print("Setting up video frame")
                # Clear video frame and show it
                for widget in self.video_frame.winfo_children():
                    widget.destroy()
                self.video_frame.pack(fill="both", expand=True)
                
                # Add loading message
                loading_label = tk.Label(self.video_frame, text="🎥 Starting camera...\nPlease wait...", 
                                       font=("Arial", 12), fg="white", bg="black")
                loading_label.pack(expand=True)
                print("Loading label added to video frame")
            
            # Start OpenCV calibration
            self.cal_instruction_label.config(text="🎥 Starting camera... Please wait...")
            print("Starting camera thread for opencv_calibration_loop")
            self.start_camera_thread(self.opencv_calibration_loop)
    
    def save_calibration(self):
        if len(self.calibration_points) != 4:
            messagebox.showerror("Error", "Need 4 calibration points!")
            return
        
        try:
            # Save calibration points
            np.save("calibration_points.npy", np.array(self.calibration_points))
            
            # Save method
            method_name = "gui_manual" if self.calibration_method.get() == "manual" else "opencv_hand_tracking"
            with open("calibration_method.txt", "w") as f:
                f.write(method_name)
            
            # Save flip setting
            with open("calibration_flip.txt", "w") as f:
                f.write("true" if self.use_flip.get() else "false")
            
            self.setup_transformation_matrix()
            self.update_calibration_status()
            
            self.status_label.config(text="✅ Calibration saved successfully!")
            messagebox.showinfo("Success", "Calibration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save calibration: {e}")
    
    def start_mouse_control(self):
        if not self.is_calibrated():
            messagebox.showerror("Error", "Please complete calibration first!")
            return
        
        if not self.camera_var.get():
            messagebox.showerror("Error", "Please select a camera first!")
            return
        
        self.selected_camera = self.get_camera_index()
        self.is_clicking = False
        self.prev_positions_x = []
        self.prev_positions_y = []
        
        # Update UI
        self.start_mouse_btn.config(state="disabled")
        self.mouse_status_label.config(text="🎥 Starting camera... Please wait...")
        
        self.start_camera_thread(self.mouse_control_loop)
    
    def start_camera_thread(self, target_function):
        print(f"start_camera_thread called with target: {target_function.__name__}")
        print(f"Current running state: {self.running}")
        
        if self.running:
            print("Camera already running, stopping first")
            self.stop_camera()
        
        print("Setting running=True and starting new thread")
        self.running = True
        self.camera_thread = threading.Thread(target=target_function, daemon=True)
        self.camera_thread.start()
        print(f"Camera thread started: {self.camera_thread}")
    
    def stop_camera(self):
        print("stop_camera called")
        self.running = False
        if self.cap:
            print("Releasing camera capture")
            self.cap.release()
            self.cap = None
        
        # Also stop manual camera feed if running
        if hasattr(self, 'manual_camera_running') and self.manual_camera_running:
            self.stop_manual_camera_feed()
        
        # Clear video displays and update UI
        self.root.after(0, self.clear_video_displays)
        
        # Update button states safely
        try:
            if hasattr(self, 'start_cal_btn') and self.start_cal_btn.winfo_exists():
                self.start_cal_btn.config(state="normal")
        except (AttributeError, tk.TclError):
            pass
        
        try:
            if hasattr(self, 'start_mouse_btn') and self.start_mouse_btn.winfo_exists():
                self.start_mouse_btn.config(state="normal")
        except (AttributeError, tk.TclError):
            pass
    
    def clear_video_displays(self):
        """Clear video displays in main thread"""
        for frame_attr in ['video_frame', 'mouse_video_frame']:
            try:
                frame = getattr(self, frame_attr, None)
                if frame and frame.winfo_exists():
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label):
                            widget.destroy()
                    
                    # Add placeholder if it's the video_frame in calibration mode
                    if frame_attr == 'video_frame' and self.current_mode == "calibration":
                        placeholder_label = tk.Label(frame, text="📹 Camera feed will appear here\nClick 'Start Calibration' to begin", 
                                                    font=("Arial", 12), fg="white", bg="black")
                        placeholder_label.pack(expand=True)
            except (AttributeError, tk.TclError):
                pass
    
    def init_camera(self, camera_index):
        """Initialize camera with given index"""
        print(f"Initializing camera {camera_index}...")
        try:
            # Try with DirectShow first
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    print(f"✅ Camera {camera_index} opened with DirectShow")
                    return cap
                cap.release()
            
            # Try without DirectShow
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    print(f"✅ Camera {camera_index} opened without DirectShow")
                    return cap
                cap.release()
        except Exception as e:
            print(f"❌ Camera {camera_index} error: {e}")
        
        print(f"❌ Failed to open camera {camera_index}")
        return None
    
    def opencv_calibration_loop(self):
        print("Starting OpenCV calibration loop...")
        self.cap = self.init_camera(self.selected_camera)
        if not self.cap:
            print("Failed to initialize camera in calibration loop")
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to open camera!"))
            self.root.after(0, lambda: self.start_cal_btn.config(state="normal"))
            self.root.after(0, lambda: self.cal_instruction_label.config(text="❌ Failed to open camera. Try different camera."))
            return
        
        print(f"Camera {self.selected_camera} opened for calibration")
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Update status
        self.root.after(0, lambda: self.cal_instruction_label.config(text="✋ Place your hand at the specified corner and hold still..."))
        
        stable_count = 0
        last_pos = None
        frame_count = 0
        
        print("Starting calibration video loop...")
        while self.running and self.current_corner < 4:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame from camera")
                break
            
            frame_count += 1
            if frame_count % 30 == 0:  # Print every 30 frames
                print(f"Processing frame {frame_count}, corner {self.current_corner}")
            
            if self.use_flip.get():
                frame = cv2.flip(frame, 1)
            
            h, w, _ = frame.shape
            
            # Draw instructions
            corner_name = self.corner_names[self.current_corner]
            cv2.putText(frame, f"Place hand at: {corner_name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Corner {self.current_corner + 1}/4", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, "Hold still for 3 seconds", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Process hand detection
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Get hand center
                    lm = landmarks.landmark[9]  # Middle finger MCP
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    cv2.circle(frame, (cx, cy), 15, (0, 0, 255), -1)
                    
                    # Check if hand is stable
                    if last_pos is None:
                        last_pos = (cx, cy)
                        stable_count = 0
                    elif abs(cx - last_pos[0]) < 20 and abs(cy - last_pos[1]) < 20:
                        stable_count += 1
                        
                        # Show countdown
                        countdown = 3 - (stable_count // 10)
                        if countdown > 0:
                            cv2.putText(frame, str(countdown), (cx + 30, cy),
                                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
                        
                        if stable_count >= 30:  # ~1 second at 30fps
                            self.calibration_points.append([cx, cy])
                            self.current_corner += 1
                            stable_count = 0
                            last_pos = None
                            print(f"Captured corner {self.current_corner}: ({cx}, {cy})")
                            
                            if self.current_corner >= 4:
                                break
                    else:
                        stable_count = 0
                        last_pos = (cx, cy)
            
            # Display frame if video_frame exists and is valid
            try:
                if hasattr(self, 'video_frame') and self.video_frame.winfo_exists():
                    if frame_count % 30 == 0:  # Debug every 30 frames
                        print(f"Attempting to display frame to video_frame")
                    self.display_frame(frame, self.video_frame)
                else:
                    if frame_count % 30 == 0:
                        print("Video frame not available for display")
            except Exception as e:
                print(f"Display frame error: {e}")
            
            # Control frame rate
            time.sleep(0.033)  # ~30 FPS
        
        print("Calibration loop ending...")
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        
        # Update UI after completion
        if len(self.calibration_points) == 4:
            print("Calibration complete!")
            self.root.after(0, lambda: self.save_cal_btn.config(state="normal"))
            self.root.after(0, lambda: self.cal_instruction_label.config(text="✅ Calibration complete! Click 'Save Calibration' to finish."))
        
        self.root.after(0, lambda: self.start_cal_btn.config(state="normal"))
        self.running = False
    
    def mouse_control_loop(self):
        self.cap = self.init_camera(self.selected_camera)
        if not self.cap:
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to open camera!"))
            self.root.after(0, lambda: self.start_mouse_btn.config(state="normal"))
            self.root.after(0, lambda: self.mouse_status_label.config(text="❌ Failed to open camera. Try different camera."))
            return
        
        print(f"Camera {self.selected_camera} opened for mouse control")
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Update status
        self.root.after(0, lambda: self.mouse_status_label.config(text="✅ Mouse control active! Move your hand to control cursor."))
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame from camera")
                break
            
            if self.use_flip.get():
                frame = cv2.flip(frame, 1)
            
            h, w, _ = frame.shape
            
            # Draw calibration area
            if len(self.calibration_points) == 4:
                points = np.array(self.calibration_points, dtype=np.int32)
                cv2.polylines(frame, [points], True, (0, 255, 255), 2)
                
                # Add labels for calibration corners
                corner_labels = ["TL", "TR", "BR", "BL"]
                for i, (point, label) in enumerate(zip(self.calibration_points, corner_labels)):
                    cv2.circle(frame, tuple(map(int, point)), 5, (0, 255, 255), -1)
                    cv2.putText(frame, label, (int(point[0]) + 10, int(point[1]) - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Process hand detection
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Get hand position (middle finger MCP)
                    lm9 = landmarks.landmark[9]
                    lm12 = landmarks.landmark[12]
                    
                    cx, cy = int(lm9.x * w), int(lm9.y * h)
                    
                    # Transform to screen coordinates
                    hand_point = np.array([[cx, cy]], dtype=np.float32).reshape(-1, 1, 2)
                    transformed = cv2.perspectiveTransform(hand_point, self.calibration_matrix)[0][0]
                    mapped_x, mapped_y = int(transformed[0]), int(transformed[1])
                    
                    # Keep within screen bounds
                    mapped_x = max(0, min(self.screen_w - 1, mapped_x))
                    mapped_y = max(0, min(self.screen_h - 1, mapped_y))
                    
                    # Smoothing
                    self.prev_positions_x.append(mapped_x)
                    self.prev_positions_y.append(mapped_y)
                    
                    smoothing_factor = self.smoothing.get()
                    if len(self.prev_positions_x) > smoothing_factor:
                        self.prev_positions_x.pop(0)
                        self.prev_positions_y.pop(0)
                    
                    if self.prev_positions_x:
                        smoothed_x = int(sum(self.prev_positions_x) / len(self.prev_positions_x))
                        smoothed_y = int(sum(self.prev_positions_y) / len(self.prev_positions_y))
                        self.mouse.position = (smoothed_x, smoothed_y)
                    
                    # Click detection (fist)
                    distance = math.sqrt((lm12.x - lm9.x)**2 + (lm12.y - lm9.y)**2)
                    hand_closed = distance < 0.00 #jarak agar terbaca klik
                    
                    if hand_closed and not self.is_clicking:
                        self.mouse.press(Button.left)
                        self.is_clicking = True
                    elif not hand_closed and self.is_clicking:
                        self.mouse.release(Button.left)
                        self.is_clicking = False
                    
                    # Visual feedback
                    color = (0, 0, 255) if hand_closed else (0, 255, 0)
                    cv2.circle(frame, (cx, cy), 15, color, -1)
                    
                    status = "CLICKING" if hand_closed else "MOVING"
                    cv2.putText(frame, status, (cx + 20, cy - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Show screen coordinates
                    cv2.putText(frame, f"Screen: {smoothed_x if self.prev_positions_x else mapped_x},{smoothed_y if self.prev_positions_y else mapped_y}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            else:
                # Reset when no hand detected
                if self.is_clicking:
                    self.mouse.release(Button.left)
                    self.is_clicking = False
                self.prev_positions_x = []
                self.prev_positions_y = []
            
            # Display frame if mouse_video_frame exists and is valid
            try:
                if hasattr(self, 'mouse_video_frame') and self.mouse_video_frame.winfo_exists():
                    self.display_frame(frame, self.mouse_video_frame)
                else:
                    print("Mouse video frame not available for display")
            except Exception as e:
                print(f"Display frame error: {e}")
            
            # Control frame rate
            time.sleep(0.033)  # ~30 FPS
        
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        
        self.root.after(0, lambda: self.start_mouse_btn.config(state="normal"))
        self.root.after(0, lambda: self.mouse_status_label.config(text="Mouse control stopped."))
        self.running = False
    
    def display_frame(self, frame, target_frame):
        """Display OpenCV frame in tkinter"""
        print(f"display_frame called - running: {self.running}, target: {target_frame}")
        
        if not self.running:
            print("Not running, returning from display_frame")
            return
        
        try:
            print(f"Processing frame for display - target_frame exists: {target_frame.winfo_exists() if hasattr(target_frame, 'winfo_exists') else 'no winfo_exists'}")
            
            # Resize frame to fit display
            display_frame = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            print(f"Image converted to PhotoImage successfully")
            
            # Update display in main thread
            def update_display():
                try:
                    print(f"Updating display in target frame: {target_frame}")
                    print(f"Target frame children count: {len(target_frame.winfo_children())}")
                    
                    # Clear existing video labels in target frame
                    for widget in target_frame.winfo_children():
                        if isinstance(widget, tk.Label):
                            print(f"Destroying existing label: {widget}")
                            widget.destroy()
                    
                    # Create new video label
                    video_label = tk.Label(target_frame, image=imgtk, bg="black")
                    video_label.image = imgtk  # Keep reference
                    video_label.pack(expand=True, fill="both")
                    
                    print(f"New video label created and packed: {video_label}")
                    
                    # Force update
                    target_frame.update_idletasks()
                    
                    print("Display update completed successfully")
                    
                except Exception as e:
                    print(f"Update display error: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Schedule update in main thread
            if self.root and self.root.winfo_exists():
                print("Scheduling display update in main thread")
                self.root.after(0, update_display)
            else:
                print("Root window not available for scheduling update")
            
        except Exception as e:
            print(f"Display error: {e}")
            import traceback
            traceback.print_exc()
    
    def on_closing(self):
        try:
            self.stop_camera()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass
    
    def start_manual_camera_feed(self):
        """Start camera feed for manual calibration background"""
        if not hasattr(self, 'manual_camera_running'):
            self.manual_camera_running = False
        
        if not self.manual_camera_running and hasattr(self, 'camera_var') and self.camera_var.get():
            print("Starting manual camera feed")
            self.manual_camera_running = True
            self.selected_camera = self.get_camera_index()
            
            # Initialize camera for manual mode
            self.manual_cap = self.init_camera(self.selected_camera)
            if self.manual_cap:
                self.update_manual_camera_background()
            else:
                print("Failed to initialize camera for manual mode")
                self.manual_camera_running = False
    
    def stop_manual_camera_feed(self):
        """Stop camera feed for manual calibration"""
        print("Stopping manual camera feed")
        self.manual_camera_running = False
        if hasattr(self, 'manual_cap') and self.manual_cap:
            self.manual_cap.release()
            self.manual_cap = None
    
    def update_manual_camera_background(self):
        """Update camera background for manual calibration"""
        if not self.manual_camera_running or not hasattr(self, 'manual_cap') or not self.manual_cap:
            return
        
        try:
            ret, frame = self.manual_cap.read()
            if ret:
                if self.use_flip.get():
                    frame = cv2.flip(frame, 1)
                
                # Resize frame to fit canvas
                if hasattr(self, 'manual_canvas'):
                    canvas_width = self.manual_canvas.winfo_width()
                    canvas_height = self.manual_canvas.winfo_height()
                    
                    if canvas_width > 1 and canvas_height > 1:
                        # Resize frame to canvas size
                        frame_resized = cv2.resize(frame, (canvas_width, canvas_height))
                        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                        self.manual_bg_photo = ImageTk.PhotoImage(img)
                        
                        # Clear canvas and draw background
                        self.manual_canvas.delete("background")
                        self.manual_canvas.create_image(0, 0, anchor="nw", image=self.manual_bg_photo, tags="background")
                        
                        # Redraw calibration points on top
                        self.draw_manual_points()
                
                # Schedule next update
                if self.manual_camera_running:
                    self.root.after(33, self.update_manual_camera_background)  # ~30 FPS
        except Exception as e:
            print(f"Manual camera background error: {e}")
            if self.manual_camera_running:
                self.root.after(100, self.update_manual_camera_background)  # Retry with longer delay
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = UltimateComfisMouse()
    app.run()
