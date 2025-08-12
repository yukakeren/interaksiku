# 🔧 Developer Documentation - Aplikasi Interaktif Sayuran

Dokumentasi teknis untuk developer yang ingin memahami atau mengembangkan aplikasi.

## 📁 Arsitektur Proyek

### Core Modules

#### 1. `calibrate_gui.py` - GUI Calibrator
```python
class CalibratorApp:
    # Main GUI application for calibration
    # - Manual drag & drop calibration
    # - OpenCV hand tracking calibration  
    # - Camera selection interface
    # - Real-time preview with overlay
```

**Key Features:**
- Dual mode calibration (Manual/OpenCV)
- Real-time camera preview
- Drag & drop interface
- Flip setting management
- Precision point system (8px radius)

#### 2. `calibrate.py` - Command Line Calibrator
```python
# Traditional command line calibration
# - Camera detection and selection
# - Hand tracking with MediaPipe
# - 4-point perspective calibration
```

#### 3. `comfis_mouse.py` - Mouse Control
```python
# Hand gesture mouse control
# - Perspective transformation
# - Smoothing algorithm
# - Click detection (fist gesture)
# - Multi-camera support
```

#### 4. `interact.py` - Main Interactive App
```python
# 6 vegetable interactive application
# - RGBA overlay system
# - Background cover-fit scaling
# - Hover detection and effects
# - Fullscreen presentation mode
```

#### 5. `interact(test).py` - Test Application
```python
# Simple test application
# - Single vegetable interaction
# - Basic functionality testing
# - Minimal resource usage
```

## 🔄 Data Flow

### Calibration Flow
```
Camera Input → Hand Detection → 4 Corner Points → Perspective Matrix → Save Files
```

**Files Generated:**
- `calibration_points.npy` - 4 corner coordinates
- `calibration_method.txt` - Method used (gui_manual/opencv_hand_tracking)
- `calibration_flip.txt` - Flip setting (true/false)

### Interaction Flow
```
Camera Input → Hand Detection → Perspective Transform → Screen Coordinates → Action
```

## 🧮 Mathematical Concepts

### Perspective Transformation
```python
# From camera coordinates to screen coordinates
M = cv2.getPerspectiveTransform(camera_corners, screen_corners)
screen_point = cv2.perspectiveTransform(camera_point, M)
```

### Smoothing Algorithm
```python
# Moving average for smooth mouse movement
prev_positions_x.append(mapped_x)
if len(prev_positions_x) > smoothing_factor:
    prev_positions_x.pop(0)
smoothed_x = sum(prev_positions_x) / len(prev_positions_x)
```

### Hand Gesture Detection
```python
# Distance calculation for fist detection
distance = math.sqrt((lm12.x - lm9.x)**2 + (lm12.y - lm9.y)**2)
hand_closed = distance < threshold  # 0.08
```

## 🎨 UI/UX Design Patterns

### Calibration Points
```python
# Color coding for corners
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 165, 255)]
# Red, Green, Blue, Orange for TL, TR, BR, BL
```

### Interactive Feedback
```python
# Hover effect with radius increase
if hovering:
    radius += 1
elif dragging:
    radius += 2
```

## 🔧 Configuration Parameters

### Camera Settings
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
```

### MediaPipe Configuration
```python
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
```

### Application Constants
```python
# Canvas dimensions
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1200

# Point configuration
point_radius = 8  # Smaller for precision
smoothing_factor = 5  # Mouse smoothing

# Gesture thresholds
fist_threshold = 0.08  # Hand closure detection
```

## 🐛 Debugging Features

### Verbose Logging
```python
print("✅ Kamera dimuat!")
print("Titik kalibrasi:", cal_points)
print("Metode kalibrasi:", calibration_method)
```

### Visual Debug Overlays
```python
# Draw calibration area
def draw_calibration_area(frame, cal_points):
    cv2.polylines(frame, [points], True, (0, 255, 255), 2)
```

### Error Handling
```python
try:
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)  # Fallback
except Exception as e:
    print(f"❌ Error: {e}")
```

## 🔄 Version Control

### File Structure for Git
```
.gitignore should include:
*.npy           # Calibration data (user-specific)
venv/           # Virtual environment
__pycache__/    # Python cache
*.pyc           # Compiled Python files
```

### Branch Strategy
- `main` - Stable release
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Bug fixes

## 🚀 Performance Optimization

### Camera Optimization
```python
# Use DirectShow for Windows performance
cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

# Set optimal resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Not too high
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

### Memory Management
```python
# Release resources properly
cap.release()
cv2.destroyAllWindows()

# Limit history for smoothing
if len(prev_positions_x) > smoothing_factor:
    prev_positions_x.pop(0)
```

### CPU Optimization
```python
# Reduce detection frequency if needed
if frame_count % 2 == 0:  # Process every 2nd frame
    results = hands.process(rgb)
```

## 🧪 Testing Guidelines

### Unit Tests
```python
# Test calibration point validation
def test_calibration_points():
    points = load_calibration()
    assert len(points) == 4
    assert all(len(p) == 2 for p in points)
```

### Integration Tests
```python
# Test camera functionality
def test_camera_detection():
    cameras = detect_cameras()
    assert len(cameras) > 0
```

### Performance Tests
```python
# Measure FPS
start_time = time.time()
# ... process frames
fps = frame_count / (time.time() - start_time)
assert fps > 15  # Minimum acceptable FPS
```

## 📦 Packaging & Distribution

### Requirements Management
```txt
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
pynput>=1.7.6
pyautogui>=0.9.54
pillow>=10.0.0
```

### Build Scripts
```batch
# setup.bat for Windows
pip install -r requirements.txt

# cross-platform installer
pip install --user -r requirements.txt
```

## 🔮 Future Development Ideas

### Enhancements
- [ ] Multi-hand support
- [ ] Gesture customization
- [ ] Voice control integration
- [ ] Machine learning gesture recognition
- [ ] Cloud calibration sync
- [ ] Mobile app companion

### Technical Improvements
- [ ] WebRTC camera support
- [ ] Hardware acceleration
- [ ] Real-time performance monitoring
- [ ] Auto-calibration with AI
- [ ] Cross-platform GUI framework

---

**For Developer Support**: Create issues on GitHub with detailed error logs and system information.
