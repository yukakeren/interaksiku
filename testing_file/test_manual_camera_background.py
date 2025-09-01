# Manual Calibration Camera Background Test
"""
Test script to verify that the manual calibration camera background functionality works.
This script creates a simple demonstration of the camera overlay feature.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time

def test_manual_camera_background():
    """Test the manual calibration camera background functionality"""
    print("Testing Manual Calibration Camera Background...")
    
    try:
        # Import our modules
        from camera_manager import CameraManager
        from ui_manager import ManualCalibrationCanvas
        from video_manager import ManualCalibrationCameraFeed
        from config import CALIBRATION
        
        print("✅ All modules imported successfully")
        
        # Create a simple test window
        root = tk.Tk()
        root.title("Manual Calibration Camera Background Test")
        root.geometry("800x600")
        
        # Create a frame for the canvas
        canvas_frame = tk.Frame(root, bg="white", relief="solid", bd=2)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create camera manager
        camera_manager = CameraManager()
        
        # Detect cameras
        print("🔍 Detecting cameras...")
        cameras = camera_manager.detect_cameras(5)  # Check first 5 cameras
        
        if not cameras:
            print("❌ No cameras found for testing")
            messagebox.showwarning("Warning", "No cameras found. The test will show the canvas without camera background.")
        else:
            print(f"✅ Found {len(cameras)} cameras")
        
        # Create a mock app controller
        class MockAppController:
            def update_manual_calibration_points(self, points):
                print(f"Updated calibration points: {points}")
        
        # Create manual calibration canvas
        mock_controller = MockAppController()
        manual_canvas = ManualCalibrationCanvas(canvas_frame, mock_controller)
        manual_canvas.create()
        
        print("✅ Manual calibration canvas created")
        
        # Create control buttons
        control_frame = tk.Frame(root)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        camera_feed = None
        
        def start_camera_background():
            nonlocal camera_feed
            if cameras:
                camera_index = cameras[0][0]  # Use first available camera
                camera_feed = ManualCalibrationCameraFeed(camera_manager, manual_canvas)
                
                if camera_feed.start(camera_index, use_flip=False):
                    print("✅ Camera background started")
                    start_btn.config(state="disabled")
                    stop_btn.config(state="normal")
                else:
                    print("❌ Failed to start camera background")
                    messagebox.showerror("Error", "Failed to start camera background")
            else:
                messagebox.showwarning("Warning", "No cameras available")
        
        def stop_camera_background():
            nonlocal camera_feed
            if camera_feed:
                camera_feed.stop()
                camera_feed = None
                print("✅ Camera background stopped")
                start_btn.config(state="normal")
                stop_btn.config(state="disabled")
        
        start_btn = tk.Button(
            control_frame,
            text="▶️ Start Camera Background",
            command=start_camera_background,
            font=("Arial", 11),
            bg="#27ae60",
            fg="white"
        )
        start_btn.pack(side="left", padx=(0, 10))
        
        stop_btn = tk.Button(
            control_frame,
            text="⏹️ Stop Camera Background",
            command=stop_camera_background,
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            state="disabled"
        )
        stop_btn.pack(side="left")
        
        # Instructions
        instruction_label = tk.Label(
            root,
            text="Instructions:\n• Click 'Start Camera Background' to overlay camera feed\n• Drag the colored points to calibrate\n• Click 'Stop Camera Background' to remove overlay",
            font=("Arial", 10),
            bg="#f0f0f0",
            justify="left"
        )
        instruction_label.pack(fill="x", padx=20, pady=10)
        
        def on_closing():
            stop_camera_background()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✅ Test window created successfully")
        print("🎉 Manual calibration camera background test ready!")
        print("Click 'Start Camera Background' to test the camera overlay feature.")
        
        # Run the test
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the manual calibration camera background test"""
    print("Manual Calibration Camera Background Test")
    print("=" * 50)
    
    success = test_manual_camera_background()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
