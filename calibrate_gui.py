import cv2
import mediapipe as mp
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading

# Set environment variables for Windows compatibility
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

class CalibratorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kalibrasi Layar Interaktif")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Variables
        self.calibration_method = tk.StringVar(value="manual")  # Default to manual method
        self.use_flip = tk.BooleanVar(value=False)  # Default to normal mode (unchecked)
        self.selected_camera = None
        self.cap = None
        self.hands = None
        self.points = []
        self.corner_names = ["Kiri Atas", "Kanan Atas", "Kanan Bawah", "Kiri Bawah"]
        self.current_corner = 0
        
        # GUI variables for manual calibration
        self.canvas_width = 640
        self.canvas_height = 480
        self.manual_points = [[80, 80], [560, 80], [560, 400], [80, 400]]  # Smaller default corners with better margin
        self.dragging = False
        self.selected_point = -1
        self.camera_frame = None
        self.point_radius = 8  # Smaller radius for easier calibration
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main title
        title_label = tk.Label(self.root, text="KALIBRASI LAYAR INTERAKTIF", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Method selection frame
        method_frame = tk.LabelFrame(self.root, text="Pilih Metode Kalibrasi", 
                                    font=("Arial", 12, "bold"))
        method_frame.pack(fill="x", padx=20, pady=10)
        
        opencv_radio = tk.Radiobutton(method_frame, 
                                     text="OpenCV - Hand Tracking (Deteksi Jari)", 
                                     variable=self.calibration_method, 
                                     value="opencv",
                                     font=("Arial", 10))
        opencv_radio.pack(anchor="w", padx=10, pady=5)
        
        manual_radio = tk.Radiobutton(method_frame, 
                                     text="Manual - GUI Drag & Drop (Geser Titik)", 
                                     variable=self.calibration_method, 
                                     value="manual",
                                     font=("Arial", 10))
        manual_radio.pack(anchor="w", padx=10, pady=5)
        
        # Camera selection frame
        camera_frame = tk.LabelFrame(self.root, text="Pilih Kamera", 
                                    font=("Arial", 12, "bold"))
        camera_frame.pack(fill="x", padx=20, pady=10)
        
        self.camera_var = tk.StringVar()
        self.camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var, 
                                        state="readonly", font=("Arial", 10))
        self.camera_combo.pack(fill="x", padx=10, pady=10)
        
        detect_button = tk.Button(camera_frame, text="Deteksi Kamera", 
                                 command=self.detect_cameras,
                                 font=("Arial", 10))
        detect_button.pack(pady=5)
        
        # Flip option frame
        flip_frame = tk.LabelFrame(self.root, text="Opsi Flip Kamera", 
                                  font=("Arial", 12, "bold"))
        flip_frame.pack(fill="x", padx=20, pady=10)
        
        flip_checkbox = tk.Checkbutton(flip_frame, 
                                      text="Mirror/Flip horizontal (Seperti selfie)", 
                                      variable=self.use_flip,
                                      font=("Arial", 10))
        flip_checkbox.pack(anchor="w", padx=10, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        start_button = tk.Button(button_frame, text="Mulai Kalibrasi", 
                                command=self.start_calibration,
                                font=("Arial", 12, "bold"),
                                bg="#4CAF50", fg="white", pady=10)
        start_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        load_button = tk.Button(button_frame, text="Load Kalibrasi", 
                               command=self.load_calibration,
                               font=("Arial", 12), pady=10)
        load_button.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        exit_button = tk.Button(button_frame, text="Keluar", 
                               command=self.exit_app,
                               font=("Arial", 12),
                               bg="#f44336", fg="white", pady=10)
        exit_button.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Status frame
        self.status_label = tk.Label(self.root, text="Siap untuk kalibrasi", 
                                    font=("Arial", 10), relief="sunken", anchor="w")
        self.status_label.pack(fill="x", side="bottom", padx=20, pady=10)
        
        # Detect cameras on startup
        self.root.after(100, self.detect_cameras)
        
    def detect_cameras(self):
        self.status_label.config(text="Mendeteksi kamera...")
        self.root.update()
        
        available_cameras = []
        
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(f"Kamera {i}")
                cap.release()
            else:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras.append(f"Kamera {i} (tanpa DirectShow)")
                    cap.release()
        
        if available_cameras:
            self.camera_combo['values'] = available_cameras
            self.camera_combo.current(0)
            self.status_label.config(text=f"Ditemukan {len(available_cameras)} kamera")
        else:
            self.status_label.config(text="Tidak ada kamera yang ditemukan!")
            
    def start_calibration(self):
        if not self.camera_var.get():
            messagebox.showerror("Error", "Pilih kamera terlebih dahulu!")
            return
            
        method = self.calibration_method.get()
        camera_text = self.camera_var.get()
        camera_index = int(camera_text.split()[1])
        
        if method == "opencv":
            self.start_opencv_calibration(camera_index)
        else:
            self.start_manual_calibration(camera_index)
            
    def start_opencv_calibration(self, camera_index):
        self.status_label.config(text="Memulai kalibrasi OpenCV...")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_index)
            
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Tidak dapat membuka kamera {camera_index}")
            return
            
        # Initialize MediaPipe
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7,
            max_num_hands=1
        )
        
        self.points = []
        self.current_corner = 0
        
        # Hide main window and start OpenCV calibration
        self.root.withdraw()
        self.opencv_calibration_loop()
        
    def opencv_calibration_loop(self):
        cv2.namedWindow("Kalibrasi OpenCV", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Kalibrasi OpenCV", 800, 600)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Apply flip setting
            if self.use_flip.get():
                frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            # Draw instructions
            if self.current_corner < len(self.corner_names):
                instruction = f"Arahkan jari ke: {self.corner_names[self.current_corner]} - Tekan SPASI"
                cv2.putText(frame, instruction, (30, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
            progress = f"Progress: {len(self.points)}/4"
            cv2.putText(frame, progress, (30, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for hand in results.multi_hand_landmarks:
                    x = int(hand.landmark[8].x * w)
                    y = int(hand.landmark[8].y * h)
                    cv2.circle(frame, (x, y), 12, (0, 255, 0), -1)
                    cv2.putText(frame, f"({x}, {y})", (x+15, y-15),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Show saved points
            for i, point in enumerate(self.points):
                cv2.circle(frame, tuple(point), 8, (255, 0, 0), -1)
                cv2.putText(frame, self.corner_names[i], (point[0]+10, point[1]-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            cv2.imshow("Kalibrasi OpenCV", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and results.multi_hand_landmarks and len(self.points) < 4:
                for hand in results.multi_hand_landmarks:
                    x = int(hand.landmark[8].x * w)
                    y = int(hand.landmark[8].y * h)
                    self.points.append([x, y])
                    self.current_corner += 1
                    print(f"{self.corner_names[len(self.points)-1]}: ({x}, {y})")
                    break
                    
            if len(self.points) == 4:
                self.save_calibration()
                break
                
            if key == 27:  # ESC
                break
                
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.deiconify()
        
    def start_manual_calibration(self, camera_index):
        self.status_label.config(text="Memulai kalibrasi manual...")
        
        # Initialize camera for preview
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_index)
            
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Tidak dapat membuka kamera {camera_index}")
            return
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
        # Create manual calibration window
        self.manual_window = tk.Toplevel(self.root)
        self.manual_window.title("Kalibrasi Manual - Drag Titik pada Preview Kamera")
        self.manual_window.geometry("800x650")
        self.manual_window.protocol("WM_DELETE_WINDOW", self.close_manual_calibration)
        
        # Instructions
        instructions = tk.Label(self.manual_window, 
                               text="Geser titik berwarna ke sudut area proyeksi yang diinginkan pada preview kamera",
                               font=("Arial", 12, "bold"), fg="blue")
        instructions.pack(pady=10)
        
        # Additional instructions
        detail_instructions = tk.Label(self.manual_window,
                                     text="Kiri Atas (Merah) → Kanan Atas (Hijau) → Kanan Bawah (Biru) → Kiri Bawah (Orange)",
                                     font=("Arial", 10))
        detail_instructions.pack(pady=5)
        
        # Camera preview with overlay calibration points
        preview_frame = tk.LabelFrame(self.manual_window, text="Preview Kamera dengan Titik Kalibrasi")
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.calibration_canvas = tk.Canvas(preview_frame, 
                                           width=self.canvas_width, 
                                           height=self.canvas_height,
                                           bg="black")
        self.calibration_canvas.pack(padx=10, pady=10)
        
        # Bind canvas events
        self.calibration_canvas.bind("<Button-1>", self.on_canvas_click)
        self.calibration_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.calibration_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.calibration_canvas.bind("<Motion>", self.on_canvas_hover)
        
        # Add cursor change for better UX
        self.calibration_canvas.config(cursor="hand2")
        
        # Control buttons for manual calibration
        manual_button_frame = tk.Frame(self.manual_window)
        manual_button_frame.pack(fill="x", padx=20, pady=10)
        
        save_manual_button = tk.Button(manual_button_frame, text="Simpan Kalibrasi", 
                                      command=self.save_manual_calibration,
                                      font=("Arial", 12, "bold"),
                                      bg="#4CAF50", fg="white", pady=5)
        save_manual_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        reset_button = tk.Button(manual_button_frame, text="Reset Posisi", 
                                command=self.reset_manual_points,
                                font=("Arial", 12), pady=5)
        reset_button.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        cancel_button = tk.Button(manual_button_frame, text="Batal", 
                                 command=self.close_manual_calibration,
                                 font=("Arial", 12),
                                 bg="#f44336", fg="white", pady=5)
        cancel_button.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Start camera preview with overlay
        self.update_camera_with_overlay()
        
    def update_camera_with_overlay(self):
        """Update camera feed with overlay calibration points"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Apply flip setting
                if self.use_flip.get():
                    frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
                
                # Draw calibration points on the frame
                colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 165, 255)]  # BGR: Red, Green, Blue, Orange
                point_names = ["Kiri Atas", "Kanan Atas", "Kanan Bawah", "Kiri Bawah"]
                
                # Draw connecting lines (calibration area) - thinner lines
                if len(self.manual_points) == 4:
                    pts = np.array(self.manual_points, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (255, 255, 0), 1)  # Thinner yellow lines
                
                # Draw calibration points
                for i, (x, y) in enumerate(self.manual_points):
                    x, y = int(x), int(y)
                    
                    # Highlight if being dragged or hovered
                    radius = self.point_radius
                    if self.selected_point == i and self.dragging:
                        radius += 2  # Smaller increase when dragging
                    elif hasattr(self, 'hover_point') and self.hover_point == i:
                        radius += 1  # Smaller increase when hovering
                    
                    # Draw outer circle (white border) - smaller
                    cv2.circle(frame, (x, y), radius + 2, (255, 255, 255), -1)
                    # Draw inner circle (colored) - smaller
                    cv2.circle(frame, (x, y), radius, colors[i], -1)
                    
                    # Draw point label - smaller font
                    label_y = y - radius - 12
                    if label_y < 20:
                        label_y = y + radius + 25
                    
                    cv2.putText(frame, point_names[i], (x - 40, label_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.putText(frame, point_names[i], (x - 40, label_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 1)
                
                # Add instruction text on the frame - smaller font
                cv2.putText(frame, "Geser titik berwarna ke sudut area proyeksi", (10, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Add coordinate info if dragging
                if self.dragging and self.selected_point != -1:
                    point_name = point_names[self.selected_point]
                    coord_text = f"Menyeret {point_name}: ({int(self.manual_points[self.selected_point][0])}, {int(self.manual_points[self.selected_point][1])})"
                    cv2.putText(frame, coord_text, (10, frame.shape[0] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Convert to PIL Image and display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                if hasattr(self, 'calibration_canvas'):
                    self.calibration_canvas.delete("all")
                    self.calibration_canvas.create_image(self.canvas_width//2, self.canvas_height//2, 
                                                        image=photo)
                    self.calibration_canvas.image = photo  # Keep a reference
                    
        if hasattr(self, 'manual_window') and self.manual_window.winfo_exists():
            self.manual_window.after(30, self.update_camera_with_overlay)
            
    def draw_calibration_points(self):
        self.calibration_canvas.delete("all")
        
        # Draw rectangle connecting the points - thinner line
        points = [tuple(p) for p in self.manual_points]
        if len(points) == 4:
            self.calibration_canvas.create_polygon(points, outline="yellow", fill="", width=1)
        
        # Draw points - smaller circles
        colors = ["red", "green", "blue", "orange"]
        for i, (x, y) in enumerate(self.manual_points):
            self.calibration_canvas.create_oval(x-6, y-6, x+6, y+6, 
                                               fill=colors[i], outline="white", width=1)
            self.calibration_canvas.create_text(x, y-15, text=self.corner_names[i], 
                                               fill="white", font=("Arial", 8, "bold"))
            
    def on_canvas_hover(self, event):
        """Handle mouse hover to highlight points"""
        x, y = event.x, event.y
        
        # Find closest point for hover effect
        min_distance = float('inf')
        closest_point = -1
        
        for i, (px, py) in enumerate(self.manual_points):
            distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
            if distance < min_distance and distance < (self.point_radius + 12):  # Slightly larger detection area
                min_distance = distance
                closest_point = i
                
        self.hover_point = closest_point if closest_point != -1 else None
        
    def on_canvas_click(self, event):
        x, y = event.x, event.y
        
        # Convert canvas coordinates to image coordinates
        # Canvas shows image centered, so we need to account for that
        img_x = x
        img_y = y
        
        # Find closest point
        min_distance = float('inf')
        closest_point = -1
        
        for i, (px, py) in enumerate(self.manual_points):
            distance = ((img_x - px) ** 2 + (img_y - py) ** 2) ** 0.5
            if distance < min_distance and distance < (self.point_radius + 8):  # Smaller tolerance for precise clicking
                min_distance = distance
                closest_point = i
                
        if closest_point != -1:
            self.selected_point = closest_point
            self.dragging = True
            
    def on_canvas_drag(self, event):
        if self.dragging and self.selected_point != -1:
            # Convert canvas coordinates to image coordinates
            x = max(self.point_radius, min(self.canvas_width - self.point_radius, event.x))
            y = max(self.point_radius, min(self.canvas_height - self.point_radius, event.y))
            
            self.manual_points[self.selected_point] = [x, y]
            
    def on_canvas_release(self, event):
        self.dragging = False
        self.selected_point = -1
        
    def reset_manual_points(self):
        """Reset calibration points to default positions with margin"""
        margin = 40  # Smaller margin for better calibration area
        self.manual_points = [
            [margin, margin],  # Top-left
            [self.canvas_width - margin, margin],  # Top-right  
            [self.canvas_width - margin, self.canvas_height - margin],  # Bottom-right
            [margin, self.canvas_height - margin]  # Bottom-left
        ]
        
    def save_manual_calibration(self):
        # Manual points are from camera preview with current flip setting
        camera_points = [[int(x), int(y)] for x, y in self.manual_points]
        
        # Save calibration points
        np.save("calibration_points.npy", np.array(camera_points))
        
        # Save metadata to indicate this is from GUI calibrator
        with open("calibration_method.txt", "w") as f:
            f.write("gui_manual")
        
        # Save flip setting
        with open("calibration_flip.txt", "w") as f:
            f.write("true" if self.use_flip.get() else "false")
            
        flip_status = "Mirror" if self.use_flip.get() else "Normal"
        messagebox.showinfo("Berhasil", 
                           "Kalibrasi manual tersimpan!\n" +
                           f"Flip setting: {flip_status}\n" +
                           f"Titik kalibrasi (koordinat preview kamera):\n" +
                           f"Kiri Atas: {camera_points[0]}\n" +
                           f"Kanan Atas: {camera_points[1]}\n" +
                           f"Kanan Bawah: {camera_points[2]}\n" +
                           f"Kiri Bawah: {camera_points[3]}\n\n" +
                           "File: calibration_points.npy")
        self.close_manual_calibration()
        
    def close_manual_calibration(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if hasattr(self, 'manual_window'):
            self.manual_window.destroy()
            
    def save_calibration(self):
        np.save("calibration_points.npy", np.array(self.points))
        
        # Save metadata to indicate this is from OpenCV hand tracking
        with open("calibration_method.txt", "w") as f:
            f.write("opencv_hand_tracking")
        
        # Save flip setting
        with open("calibration_flip.txt", "w") as f:
            f.write("true" if self.use_flip.get() else "false")
            
        print("\n" + "="*50)
        print("✅ KALIBRASI BERHASIL!")
        print("File tersimpan: calibration_points.npy")
        print(f"Flip setting: {'Mirror' if self.use_flip.get() else 'Normal'}")
        print("Titik kalibrasi:")
        for i, point in enumerate(self.points):
            print(f"  {self.corner_names[i]}: {point}")
        print("="*50)
        
        messagebox.showinfo("Berhasil", 
                           "Kalibrasi OpenCV tersimpan!\n" +
                           "File: calibration_points.npy")
                           
    def load_calibration(self):
        try:
            points = np.load("calibration_points.npy")
            info = "Kalibrasi yang tersimpan:\n\n"
            for i, point in enumerate(points):
                info += f"{self.corner_names[i]}: {point}\n"
            messagebox.showinfo("Kalibrasi Tersimpan", info)
        except FileNotFoundError:
            messagebox.showerror("Error", "File kalibrasi tidak ditemukan!")
            
    def exit_app(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CalibratorApp()
    app.run()
