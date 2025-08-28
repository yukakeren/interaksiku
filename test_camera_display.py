import cv2
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading
import time

class SimpleCameraTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Display Test")
        self.root.geometry("800x600")
        
        self.cap = None
        self.running = False
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Camera selection
        self.camera_var = tk.StringVar()
        self.camera_combo = ttk.Combobox(control_frame, textvariable=self.camera_var, state="readonly")
        self.camera_combo.pack(side="left", padx=5)
        
        detect_btn = tk.Button(control_frame, text="Detect Cameras", command=self.detect_cameras)
        detect_btn.pack(side="left", padx=5)
        
        start_btn = tk.Button(control_frame, text="Start Camera", command=self.start_camera)
        start_btn.pack(side="left", padx=5)
        
        stop_btn = tk.Button(control_frame, text="Stop Camera", command=self.stop_camera)
        stop_btn.pack(side="left", padx=5)
        
        # Video frame
        self.video_frame = tk.Frame(self.root, bg="black", width=640, height=480)
        self.video_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Status
        self.status_label = tk.Label(self.root, text="Click 'Detect Cameras' to start")
        self.status_label.pack()
        
        # Detect cameras on startup
        self.detect_cameras()
    
    def detect_cameras(self):
        self.status_label.config(text="Detecting cameras...")
        self.root.update()
        
        available_cameras = []
        
        for i in range(5):
            try:
                print(f"Testing camera {i}...")
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        available_cameras.append(f"Camera {i}")
                        print(f"✅ Camera {i}: Working")
                    cap.release()
                else:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            available_cameras.append(f"Camera {i}")
                            print(f"✅ Camera {i}: Working (no DirectShow)")
                        cap.release()
            except Exception as e:
                print(f"❌ Camera {i}: Error - {e}")
        
        if available_cameras:
            self.camera_combo['values'] = available_cameras
            self.camera_combo.current(0)
            self.status_label.config(text=f"Found {len(available_cameras)} cameras")
        else:
            self.status_label.config(text="No cameras found!")
    
    def get_camera_index(self):
        camera_text = self.camera_var.get()
        if camera_text:
            try:
                return int(camera_text.split()[1])
            except:
                return 0
        return 0
    
    def start_camera(self):
        if self.running:
            return
        
        camera_index = self.get_camera_index()
        print(f"Starting camera {camera_index}")
        
        self.running = True
        self.camera_thread = threading.Thread(target=self.camera_loop, args=(camera_index,))
        self.camera_thread.daemon = True
        self.camera_thread.start()
    
    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear video display
        for widget in self.video_frame.winfo_children():
            widget.destroy()
    
    def camera_loop(self, camera_index):
        try:
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(camera_index)
            
            if not self.cap.isOpened():
                self.root.after(0, lambda: messagebox.showerror("Error", f"Cannot open camera {camera_index}"))
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.root.after(0, lambda: self.status_label.config(text=f"Camera {camera_index} running"))
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                
                # Add some text to verify the frame is live
                cv2.putText(frame, f"Camera {camera_index} - Live", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                self.display_frame(frame)
                time.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            print(f"Camera loop error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Camera error: {e}"))
        finally:
            if self.cap:
                self.cap.release()
                self.cap = None
    
    def display_frame(self, frame):
        try:
            # Resize and convert frame
            frame_resized = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            def update_display():
                try:
                    # Clear old display
                    for widget in self.video_frame.winfo_children():
                        widget.destroy()
                    
                    # Create new label
                    label = tk.Label(self.video_frame, image=imgtk)
                    label.image = imgtk  # Keep reference
                    label.pack(expand=True)
                    
                except Exception as e:
                    print(f"Update display error: {e}")
            
            self.root.after(0, update_display)
            
        except Exception as e:
            print(f"Display frame error: {e}")
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        self.stop_camera()
        self.root.destroy()

if __name__ == "__main__":
    app = SimpleCameraTest()
    app.run()
