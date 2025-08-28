# Ultimate Comfis Mouse - Installation Guide

## Prerequisites
- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)
- Webcam or USB camera

## Installation Steps

### 1. Clone or Download the Project
```bash
git clone [repository-url]
cd interaksiku
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
# or
.\venv\Scripts\activate.bat  # On Windows Command Prompt
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Alternative: Install Dependencies Manually
```bash
pip install opencv-python>=4.8.0
pip install mediapipe>=0.10.0
pip install numpy>=1.24.0
pip install pynput>=1.7.6
pip install pyautogui>=0.9.54
pip install Pillow>=10.0.0
```

### 4. Run the Application
```bash
python ultimate_comfis_mouse.py
```

Or use the provided batch file:
```bash
.\run_ultimate_comfis_mouse.bat
```

## Features
- **Unified Interface**: Combines calibration and mouse control in one application
- **Dual Calibration Modes**: 
  - Manual calibration with live camera background
  - OpenCV hand tracking calibration
- **Real-time Hand Tracking**: MediaPipe-powered hand detection
- **Multi-camera Support**: Works with multiple USB cameras
- **Customizable Settings**: Adjustable sensitivity, smoothing, and flip options

## Usage
1. **Calibration Tab**: Set up your tracking area
   - Choose between Manual or OpenCV calibration
   - Select your camera
   - Define the 4 corners of your tracking area
2. **Mouse Control Tab**: Start hand tracking mouse control
   - Uses the calibrated area for accurate tracking
   - Real-time cursor control with hand movements

## Troubleshooting
- Ensure camera permissions are granted
- Try different camera indices if camera doesn't work
- Run as administrator if permission issues occur
- Check that all dependencies are properly installed

## System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: Multi-core processor for smooth performance
- **Camera**: Any USB webcam or built-in camera
- **OS**: Windows 10/11
