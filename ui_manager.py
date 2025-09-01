# User Interface components and layouts
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import math
from typing import Callable, Optional, List, Tuple
from config import COLORS, FONTS, CALIBRATION


class UIManager:
    """Manages the main user interface"""
    
    def __init__(self, root: tk.Tk, app_controller):
        self.root = root
        self.app_controller = app_controller
        self.current_mode = "home"
        
        # UI References
        self.mode_buttons = {}
        self.video_container = None
        self.status_label = None
        self.cal_status_label = None
        self.cal_instruction_label = None
        self.mouse_status_label = None
        
        # Video frames
        self.video_frame = None
        self.mouse_video_frame = None
        self.manual_frame = None
        self.manual_canvas = None
        self.right_panel = None
        
        # Control buttons
        self.start_cal_btn = None
        self.save_cal_btn = None
        self.start_mouse_btn = None
        
    def setup_main_window(self) -> None:
        """Setup main window and basic layout"""
        self.root.title("Ultimate Comfis Mouse - Calibration & Control")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS['background'])
        
        self._create_header()
        self._create_main_layout()
        self._create_status_bar()
        
        # Show home content by default
        self.switch_mode("home")
    
    def _create_header(self) -> None:
        """Create header section"""
        header_frame = tk.Frame(self.root, bg=COLORS['primary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🖱️ ULTIMATE COMFIS MOUSE",
            font=FONTS['title'], 
            fg=COLORS['white'], 
            bg=COLORS['primary']
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="All-in-One Hand Tracking Calibration & Mouse Control",
            font=FONTS['subtitle'],
            fg=COLORS['light'],
            bg=COLORS['primary']
        )
        subtitle_label.pack()
    
    def _create_main_layout(self) -> None:
        """Create main layout with left panel and right panel"""
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Controls
        left_panel = self._create_left_panel(main_frame)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        
        # Right panel - Content
        self.right_panel = tk.Frame(main_frame, bg=COLORS['white'], relief="solid", bd=1)
        self.right_panel.pack(side="right", fill="both", expand=True)
    
    def _create_left_panel(self, parent: tk.Widget) -> tk.Frame:
        """Create left control panel"""
        left_panel = tk.Frame(parent, bg=COLORS['background'], width=350)
        left_panel.pack_propagate(False)
        
        # Mode selection
        self._create_mode_selection(left_panel)
        
        # Settings
        self._create_settings_section(left_panel)
        
        # Calibration status
        self._create_calibration_status(left_panel)
        
        return left_panel
    
    def _create_mode_selection(self, parent: tk.Widget) -> None:
        """Create mode selection buttons"""
        mode_frame = tk.LabelFrame(
            parent, 
            text="🎯 Mode Selection", 
            font=FONTS['heading'], 
            bg=COLORS['background']
        )
        mode_frame.pack(fill="x", pady=(0, 15))
        
        modes = [
            ("home", "🏠 Home", COLORS['secondary']),
            ("calibration", "📐 Calibration", COLORS['danger']),
            ("mouse_control", "🖱️ Mouse Control", COLORS['success'])
        ]
        
        for mode_id, text, color in modes:
            btn = tk.Button(
                mode_frame,
                text=text,
                command=lambda m=mode_id: self.switch_mode(m),
                font=FONTS['button'],
                width=25,
                height=2,
                bg=color,
                fg=COLORS['white']
            )
            btn.pack(pady=5, padx=10)
            self.mode_buttons[mode_id] = btn
    
    def _create_settings_section(self, parent: tk.Widget) -> None:
        """Create settings section"""
        settings_frame = tk.LabelFrame(
            parent, 
            text="⚙️ Settings", 
            font=FONTS['heading'], 
            bg=COLORS['background']
        )
        settings_frame.pack(fill="x", pady=(0, 15))
        
        # Camera selection
        self._create_camera_selection(settings_frame)
        
        # Flip option
        self._create_flip_option(settings_frame)
        
        # Calibration method
        self._create_calibration_method(settings_frame)
        
        # Smoothing
        self._create_smoothing_option(settings_frame)
    
    def _create_camera_selection(self, parent: tk.Widget) -> None:
        """Create camera selection controls"""
        tk.Label(
            parent, 
            text="📷 Camera:", 
            font=FONTS['normal'], 
            bg=COLORS['background']
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        camera_frame = tk.Frame(parent, bg=COLORS['background'])
        camera_frame.pack(fill="x", padx=10)
        
        self.camera_var = tk.StringVar()
        self.camera_combo = ttk.Combobox(
            camera_frame, 
            textvariable=self.camera_var, 
            state="readonly", 
            width=20
        )
        self.camera_combo.pack(side="left", fill="x", expand=True)
        
        detect_btn = tk.Button(
            camera_frame,
            text="🔍",
            command=self.app_controller.detect_cameras,
            font=FONTS['small'],
            width=3
        )
        detect_btn.pack(side="right", padx=(5, 0))
    
    def _create_flip_option(self, parent: tk.Widget) -> None:
        """Create flip option checkbox"""
        tk.Label(
            parent, 
            text="🔄 Display:", 
            font=FONTS['normal'], 
            bg=COLORS['background']
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        self.use_flip = tk.BooleanVar(value=False)
        flip_checkbox = tk.Checkbutton(
            parent,
            text="Mirror/Flip horizontal",
            variable=self.use_flip,
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        flip_checkbox.pack(anchor="w", padx=20)
    
    def _create_calibration_method(self, parent: tk.Widget) -> None:
        """Create calibration method selection"""
        tk.Label(
            parent, 
            text="📏 Calibration Method:", 
            font=FONTS['normal'], 
            bg=COLORS['background']
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        method_frame = tk.Frame(parent, bg=COLORS['background'])
        method_frame.pack(fill="x", padx=20)
        
        self.calibration_method = tk.StringVar(value="manual")
        
        tk.Radiobutton(
            method_frame,
            text="Manual (Drag & Drop)",
            variable=self.calibration_method,
            value="manual",
            font=FONTS['small'],
            bg=COLORS['background'],
            command=self.app_controller.update_calibration_mode
        ).pack(anchor="w")
        
        tk.Radiobutton(
            method_frame,
            text="OpenCV Hand Tracking",
            variable=self.calibration_method,
            value="opencv",
            font=FONTS['small'],
            bg=COLORS['background'],
            command=self.app_controller.update_calibration_mode
        ).pack(anchor="w")
    
    def _create_smoothing_option(self, parent: tk.Widget) -> None:
        """Create smoothing option"""
        tk.Label(
            parent, 
            text="🎯 Mouse Smoothing:", 
            font=FONTS['normal'], 
            bg=COLORS['background']
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        smoothing_frame = tk.Frame(parent, bg=COLORS['background'])
        smoothing_frame.pack(fill="x", padx=20)
        
        self.smoothing = tk.IntVar(value=5)
        tk.Scale(
            smoothing_frame,
            from_=1,
            to=10,
            orient="horizontal",
            variable=self.smoothing,
            length=200,
            bg=COLORS['background']
        ).pack()
        
        tk.Label(
            smoothing_frame,
            text="1=Fast, 10=Smooth",
            font=("Arial", 8),
            fg="gray",
            bg=COLORS['background']
        ).pack()
    
    def _create_calibration_status(self, parent: tk.Widget) -> None:
        """Create calibration status display"""
        self.cal_status_frame = tk.LabelFrame(
            parent, 
            text="📊 Calibration Status", 
            font=FONTS['heading'], 
            bg=COLORS['background']
        )
        self.cal_status_frame.pack(fill="x", pady=(0, 15))
        
        self.cal_status_label = tk.Label(
            self.cal_status_frame,
            text="❌ Not Calibrated",
            font=FONTS['normal'],
            fg="red",
            bg=COLORS['background']
        )
        self.cal_status_label.pack(pady=10)
    
    def _create_status_bar(self) -> None:
        """Create status bar"""
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=FONTS['normal'],
            bd=1,
            relief="sunken",
            anchor="w",
            bg=COLORS['light']
        )
        self.status_label.pack(fill="x", side="bottom")
    
    def switch_mode(self, mode: str) -> None:
        """Switch to different mode"""
        self.current_mode = mode
        self._update_mode_buttons()
        self._clear_right_panel()
        
        if mode == "home":
            self._show_home_content()
        elif mode == "calibration":
            self._show_calibration_content()
        elif mode == "mouse_control":
            self._show_mouse_control_content()
    
    def _update_mode_buttons(self) -> None:
        """Update mode button appearances"""
        normal_colors = {
            "home": COLORS['secondary'],
            "calibration": COLORS['danger'],
            "mouse_control": COLORS['success']
        }
        
        selected_colors = {
            "home": "#2980b9",
            "calibration": "#c0392b",
            "mouse_control": "#229954"
        }
        
        for mode_id, btn in self.mode_buttons.items():
            if mode_id == self.current_mode:
                btn.config(bg=selected_colors[mode_id])
            else:
                btn.config(bg=normal_colors[mode_id])
    
    def _clear_right_panel(self) -> None:
        """Clear right panel content"""
        for widget in self.right_panel.winfo_children():
            widget.destroy()
    
    def _show_home_content(self) -> None:
        """Show home/welcome content"""
        home_content = HomeContent(self.right_panel, self.app_controller)
        home_content.create()
    
    def _show_calibration_content(self) -> None:
        """Show calibration content"""
        calibration_content = CalibrationContent(self.right_panel, self)
        calibration_content.create()
    
    def _show_mouse_control_content(self) -> None:
        """Show mouse control content"""
        mouse_content = MouseControlContent(self.right_panel, self)
        mouse_content.create()
    
    def update_calibration_status(self, is_calibrated: bool) -> None:
        """Update calibration status display"""
        if is_calibrated:
            self.cal_status_label.config(text="✅ Calibrated", fg="green")
        else:
            self.cal_status_label.config(text="❌ Not Calibrated", fg="red")
    
    def update_status(self, message: str) -> None:
        """Update status bar message"""
        self.status_label.config(text=message)


class HomeContent:
    """Home/Welcome content display"""
    
    def __init__(self, parent: tk.Widget, app_controller):
        self.parent = parent
        self.app_controller = app_controller
    
    def create(self) -> None:
        """Create home content"""
        welcome_frame = tk.Frame(self.parent, bg=COLORS['white'])
        welcome_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(
            welcome_frame,
            text="🎉 Welcome to Ultimate Comfis Mouse!",
            font=("Arial", 18, "bold"),
            bg=COLORS['white']
        ).pack(pady=(0, 20))
        
        # Description
        desc_text = """
This application combines calibration and mouse control into one easy-to-use interface.

🔹 CALIBRATION: Set up your camera and define the tracking area
🔹 MOUSE CONTROL: Use hand gestures to control your mouse cursor

Follow these steps:
        """
        tk.Label(
            welcome_frame,
            text=desc_text,
            font=FONTS['subtitle'],
            bg=COLORS['white'],
            justify="left"
        ).pack(pady=(0, 20))
        
        # Steps
        self._create_steps(welcome_frame)
        
        # System info
        self._create_system_info(welcome_frame)
    
    def _create_steps(self, parent: tk.Widget) -> None:
        """Create step-by-step instructions"""
        steps_frame = tk.Frame(parent, bg=COLORS['white'])
        steps_frame.pack(fill="x")
        
        steps = [
            ("1️⃣", "Select your camera from the dropdown"),
            ("2️⃣", "Go to Calibration mode and set up tracking area"),
            ("3️⃣", "Switch to Mouse Control mode to start using"),
        ]
        
        for emoji, step in steps:
            step_frame = tk.Frame(steps_frame, bg=COLORS['white'])
            step_frame.pack(fill="x", pady=5)
            
            tk.Label(
                step_frame,
                text=emoji,
                font=("Arial", 14),
                bg=COLORS['white']
            ).pack(side="left", padx=(0, 10))
            
            tk.Label(
                step_frame,
                text=step,
                font=("Arial", 11),
                bg=COLORS['white']
            ).pack(side="left")
    
    def _create_system_info(self, parent: tk.Widget) -> None:
        """Create system information display"""
        info_frame = tk.LabelFrame(
            parent,
            text="📊 System Information",
            bg=COLORS['white'],
            font=("Arial", 11, "bold")
        )
        info_frame.pack(fill="x", pady=(30, 0))
        
        screen_w, screen_h = self.app_controller.get_screen_size()
        info_text = f"""
Screen Resolution: {screen_w} x {screen_h}
MediaPipe: ✅ Available
OpenCV: ✅ Available
        """
        tk.Label(
            info_frame,
            text=info_text,
            font=FONTS['normal'],
            bg=COLORS['white'],
            justify="left"
        ).pack(padx=10, pady=10)


class CalibrationContent:
    """Calibration content display"""
    
    def __init__(self, parent: tk.Widget, ui_manager: UIManager):
        self.parent = parent
        self.ui_manager = ui_manager
        self.app_controller = ui_manager.app_controller
    
    def create(self) -> None:
        """Create calibration content"""
        cal_frame = tk.Frame(self.parent, bg=COLORS['white'])
        cal_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            cal_frame,
            text="📐 Camera Calibration",
            font=("Arial", 16, "bold"),
            bg=COLORS['white']
        ).pack(pady=(0, 10))
        
        # Instructions
        self._create_instructions(cal_frame)
        
        # Control buttons
        self._create_control_buttons(cal_frame)
        
        # Video/Canvas container
        self._create_video_container(cal_frame)
        
        # Status
        self.ui_manager.cal_instruction_label = tk.Label(
            cal_frame,
            text="Select camera and click 'Start Calibration'",
            font=FONTS['normal'],
            bg=COLORS['white'],
            fg="gray"
        )
        self.ui_manager.cal_instruction_label.pack()
    
    def _create_instructions(self, parent: tk.Widget) -> None:
        """Create instruction text"""
        method = self.ui_manager.calibration_method.get()
        if method == "manual":
            instruction_text = "🖱️ MANUAL MODE: Drag the colored points to the corners of your tracking area"
        else:
            instruction_text = "✋ OPENCV MODE: Follow the on-screen instructions to place your hand at each corner"
        
        tk.Label(
            parent,
            text=instruction_text,
            font=("Arial", 11),
            bg=COLORS['white'],
            fg="blue"
        ).pack(pady=(0, 15))
    
    def _create_control_buttons(self, parent: tk.Widget) -> None:
        """Create control buttons"""
        control_frame = tk.Frame(parent, bg=COLORS['white'])
        control_frame.pack(fill="x", pady=(0, 15))
        
        self.ui_manager.start_cal_btn = tk.Button(
            control_frame,
            text="▶️ Start Calibration",
            command=self.app_controller.start_calibration,
            font=FONTS['button'],
            bg=COLORS['success'],
            fg=COLORS['white'],
            width=20
        )
        self.ui_manager.start_cal_btn.pack(side="left", padx=(0, 10))
        
        self.ui_manager.save_cal_btn = tk.Button(
            control_frame,
            text="💾 Save Calibration",
            command=self.app_controller.save_calibration,
            font=FONTS['button'],
            bg=COLORS['secondary'],
            fg=COLORS['white'],
            width=20,
            state="disabled"
        )
        self.ui_manager.save_cal_btn.pack(side="left", padx=(0, 10))
        
        stop_cal_btn = tk.Button(
            control_frame,
            text="⏹️ Stop",
            command=self.app_controller.stop_camera,
            font=FONTS['button'],
            bg=COLORS['danger'],
            fg=COLORS['white'],
            width=15
        )
        stop_cal_btn.pack(side="left")
    
    def _create_video_container(self, parent: tk.Widget) -> None:
        """Create video/canvas container"""
        self.ui_manager.video_container = tk.Frame(parent, bg=COLORS['white'])
        self.ui_manager.video_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create frames for different modes
        self.ui_manager.video_frame = tk.Frame(
            self.ui_manager.video_container,
            bg=COLORS['black'],
            relief="solid",
            bd=2
        )
        
        self.ui_manager.manual_frame = tk.Frame(
            self.ui_manager.video_container,
            bg=COLORS['white'],
            relief="solid",
            bd=2
        )
        
        # Show appropriate frame
        self._show_appropriate_frame()
    
    def _show_appropriate_frame(self) -> None:
        """Show frame based on calibration method"""
        method = self.ui_manager.calibration_method.get()
        
        if method == "manual":
            self.ui_manager.manual_frame.pack(fill="both", expand=True)
            self._setup_manual_canvas()
        else:
            self.ui_manager.video_frame.pack(fill="both", expand=True)
            self._add_placeholder()
    
    def _setup_manual_canvas(self) -> None:
        """Setup manual calibration canvas"""
        canvas = ManualCalibrationCanvas(
            self.ui_manager.manual_frame,
            self.app_controller
        )
        canvas.create()
        self.ui_manager.manual_canvas = canvas
    
    def _add_placeholder(self) -> None:
        """Add placeholder for camera feed"""
        placeholder_label = tk.Label(
            self.ui_manager.video_frame,
            text="📹 Camera feed will appear here\nClick 'Start Calibration' to begin",
            font=FONTS['subtitle'],
            fg=COLORS['white'],
            bg=COLORS['black']
        )
        placeholder_label.pack(expand=True)


class MouseControlContent:
    """Mouse control content display"""
    
    def __init__(self, parent: tk.Widget, ui_manager: UIManager):
        self.parent = parent
        self.ui_manager = ui_manager
        self.app_controller = ui_manager.app_controller
    
    def create(self) -> None:
        """Create mouse control content"""
        mouse_frame = tk.Frame(self.parent, bg=COLORS['white'])
        mouse_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            mouse_frame,
            text="🖱️ Mouse Control",
            font=("Arial", 16, "bold"),
            bg=COLORS['white']
        ).pack(pady=(0, 10))
        
        # Check if calibrated
        if not self.app_controller.is_calibrated():
            self._show_calibration_required(mouse_frame)
            return
        
        # Instructions
        self._create_instructions(mouse_frame)
        
        # Control buttons
        self._create_control_buttons(mouse_frame)
        
        # Video frame
        self._create_video_frame(mouse_frame)
        
        # Status
        self.ui_manager.mouse_status_label = tk.Label(
            mouse_frame,
            text="Click 'Start Mouse Control' to begin",
            font=FONTS['normal'],
            bg=COLORS['white'],
            fg="gray"
        )
        self.ui_manager.mouse_status_label.pack()
    
    def _show_calibration_required(self, parent: tk.Widget) -> None:
        """Show calibration required message"""
        tk.Label(
            parent,
            text="⚠️ Please complete calibration first!",
            font=FONTS['subtitle'],
            bg=COLORS['white'],
            fg="red"
        ).pack(pady=20)
        
        cal_btn = tk.Button(
            parent,
            text="📐 Go to Calibration",
            command=lambda: self.ui_manager.switch_mode("calibration"),
            font=FONTS['subtitle'],
            bg=COLORS['danger'],
            fg=COLORS['white']
        )
        cal_btn.pack()
    
    def _create_instructions(self, parent: tk.Widget) -> None:
        """Create instruction text"""
        instruction_text = """
✋ Instructions:
• Move your hand in the calibrated area to control the cursor
• Make a fist to click (close your hand)
• Keep your hand visible to the camera
        """
        tk.Label(
            parent,
            text=instruction_text,
            font=("Arial", 11),
            bg=COLORS['white'],
            justify="left"
        ).pack(pady=(0, 15))
    
    def _create_control_buttons(self, parent: tk.Widget) -> None:
        """Create control buttons"""
        control_frame = tk.Frame(parent, bg=COLORS['white'])
        control_frame.pack(fill="x", pady=(0, 15))
        
        self.ui_manager.start_mouse_btn = tk.Button(
            control_frame,
            text="▶️ Start Mouse Control",
            command=self.app_controller.start_mouse_control,
            font=FONTS['button'],
            bg=COLORS['success'],
            fg=COLORS['white'],
            width=20
        )
        self.ui_manager.start_mouse_btn.pack(side="left", padx=(0, 10))
        
        stop_mouse_btn = tk.Button(
            control_frame,
            text="⏹️ Stop",
            command=self.app_controller.stop_camera,
            font=FONTS['button'],
            bg=COLORS['danger'],
            fg=COLORS['white'],
            width=15
        )
        stop_mouse_btn.pack(side="left")
    
    def _create_video_frame(self, parent: tk.Widget) -> None:
        """Create video frame"""
        self.ui_manager.mouse_video_frame = tk.Frame(
            parent,
            bg=COLORS['black'],
            relief="solid",
            bd=2
        )
        self.ui_manager.mouse_video_frame.pack(fill="both", expand=True, pady=(0, 10))


class ManualCalibrationCanvas:
    """Manual calibration drag-and-drop canvas"""
    
    def __init__(self, parent: tk.Widget, app_controller):
        self.parent = parent
        self.app_controller = app_controller
        self.canvas = None
        self.manual_calibration = None
        self.manual_bg_photo = None  # Store background camera image
        
    def create(self) -> None:
        """Create manual calibration canvas"""
        from calibration_manager import ManualCalibration
        
        self.manual_calibration = ManualCalibration()
        
        self.canvas = tk.Canvas(
            self.parent,
            width=CALIBRATION['canvas_width'],
            height=CALIBRATION['canvas_height'],
            bg=COLORS['black']
        )
        self.canvas.pack(expand=True)
        
        # Bind events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        
        self._draw_points()
    
    def _draw_points(self) -> None:
        """Draw calibration points on canvas"""
        # Clear existing points
        self.canvas.delete("points")
        self.canvas.delete("grid")
        self.canvas.delete("overlay")
        
        # Draw background grid
        self._draw_grid()
        
        # Draw calibration area
        self._draw_calibration_area()
        
        # Draw points
        self._draw_corner_points()
    
    def _draw_grid(self) -> None:
        """Draw background grid"""
        # Only draw grid if no camera background
        if not hasattr(self, 'manual_bg_photo') or self.manual_bg_photo is None:
            for i in range(0, CALIBRATION['canvas_width'], 50):
                self.canvas.create_line(
                    i, 0, i, CALIBRATION['canvas_height'],
                    fill="#d0d0d0", width=1, tags="grid"
                )
            for i in range(0, CALIBRATION['canvas_height'], 50):
                self.canvas.create_line(
                    0, i, CALIBRATION['canvas_width'], i,
                    fill="#d0d0d0", width=1, tags="grid"
                )
    
    def _draw_calibration_area(self) -> None:
        """Draw calibration area polygon"""
        points = self.manual_calibration.get_points()
        if len(points) == 4:
            flat_points = []
            for point in points:
                flat_points.extend(point)
            self.canvas.create_polygon(
                flat_points,
                outline="yellow",
                width=3,
                fill="",
                stipple="gray25",
                tags="overlay"
            )
    
    def _draw_corner_points(self) -> None:
        """Draw corner points"""
        colors = ["red", "green", "blue", "orange"]
        points = self.manual_calibration.get_points()
        
        for i, (point, color) in enumerate(zip(points, colors)):
            x, y = point
            r = CALIBRATION['point_radius']
            if getattr(self.manual_calibration, 'selected_point', -1) == i:
                r += 4
            
            self.canvas.create_oval(
                x-r, y-r, x+r, y+r,
                fill=color,
                outline=COLORS['white'],
                width=3,
                tags="points"
            )
            self.canvas.create_text(
                x, y-r-15,
                text=CALIBRATION['corner_names'][i],
                fill=color,
                font=FONTS['small'],
                tags="points"
            )
    
    def _on_click(self, event) -> None:
        """Handle canvas click"""
        closest_point = self.manual_calibration.find_closest_point(event.x, event.y)
        
        if closest_point != -1:
            self.manual_calibration.selected_point = closest_point
            self.manual_calibration.dragging = True
            self._draw_points()
    
    def _on_drag(self, event) -> None:
        """Handle canvas drag"""
        if (self.manual_calibration.dragging and 
            getattr(self.manual_calibration, 'selected_point', -1) != -1):
            self.manual_calibration.update_point(
                self.manual_calibration.selected_point,
                event.x,
                event.y
            )
            self._draw_points()
    
    def _on_release(self, event) -> None:
        """Handle canvas release"""
        self.manual_calibration.dragging = False
        self.manual_calibration.selected_point = -1
        self._draw_points()
        
        # Update app controller with new points
        points = self.manual_calibration.get_points()
        if len(points) == 4:
            self.app_controller.update_manual_calibration_points(points)
    
    def update_camera_background(self, frame) -> None:
        """Update camera background on canvas"""
        try:
            if not self.canvas or not self.canvas.winfo_exists():
                return
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # Resize frame to canvas size
                import cv2
                from PIL import Image, ImageTk
                
                frame_resized = cv2.resize(frame, (canvas_width, canvas_height))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                self.manual_bg_photo = ImageTk.PhotoImage(img)
                
                # Clear canvas and draw background
                self.canvas.delete("background")
                self.canvas.create_image(0, 0, anchor="nw", image=self.manual_bg_photo, tags="background")
                
                # Redraw calibration points on top
                self._draw_points()
        except Exception as e:
            print(f"Camera background update error: {e}")
    
    def clear_camera_background(self) -> None:
        """Clear camera background"""
        self.manual_bg_photo = None
        if self.canvas:
            self.canvas.delete("background")
            self._draw_points()  # Redraw with grid background
