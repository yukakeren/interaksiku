# Camera management utilities
import cv2
from typing import Optional, List, Tuple

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not available. Using default screen size.")


class CameraManager:
    """Handles camera detection and initialization"""
    
    def __init__(self):
        if PYAUTOGUI_AVAILABLE:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = 1920, 1080  # Default fallback
    
    def detect_cameras(self, max_cameras: int = 10) -> List[Tuple[int, str]]:
        """
        Detect available cameras
        
        Args:
            max_cameras: Maximum number of cameras to check
            
        Returns:
            List of tuples (camera_index, camera_name)
        """
        available_cameras = []
        
        for i in range(max_cameras):
            try:
                print(f"Testing camera {i}...")
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        camera_name = self._get_camera_name(cap, i)
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
        
        return available_cameras
    
    def _get_camera_name(self, cap: cv2.VideoCapture, index: int) -> str:
        """Get camera name with backend information"""
        try:
            backend_name = cap.getBackendName()
            if backend_name == "DSHOW":
                return f"Camera {index} (DirectShow)"
            else:
                return f"Camera {index} ({backend_name})"
        except:
            return f"Camera {index}"
    
    def initialize_camera(self, camera_index: int) -> Optional[cv2.VideoCapture]:
        """
        Initialize camera with given index
        
        Args:
            camera_index: Index of camera to initialize
            
        Returns:
            VideoCapture object or None if failed
        """
        print(f"Initializing camera {camera_index}...")
        try:
            # Try with DirectShow first
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    self._configure_camera(cap)
                    print(f"✅ Camera {camera_index} opened with DirectShow")
                    return cap
                cap.release()
            
            # Try without DirectShow
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    self._configure_camera(cap)
                    print(f"✅ Camera {camera_index} opened without DirectShow")
                    return cap
                cap.release()
        except Exception as e:
            print(f"❌ Camera {camera_index} error: {e}")
        
        print(f"❌ Failed to open camera {camera_index}")
        return None
    
    def _configure_camera(self, cap: cv2.VideoCapture) -> None:
        """Configure camera settings"""
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
