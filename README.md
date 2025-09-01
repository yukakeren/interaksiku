# 🖱️ Ultimate Comfis Mouse

A powerful hand tracking mouse control application that allows you to control your computer cursor using hand gestures. Perfect for presentations, accessibility needs, or just having fun with gesture-based computing!

## ✨ Features

- **🎯 Real-time Hand Tracking**: Uses advanced MediaPipe technology for accurate hand detection
- **🖱️ Gesture Mouse Control**: Control your cursor with natural hand movements
- **📐 Dual Calibration Methods**:
  - **Manual**: Easy drag-and-drop interface for quick setup
  - **OpenCV**: Automated hand tracking-based calibration
- **📷 Smart Camera Detection**: Automatically detects and supports multiple cameras
- **🎛️ Customizable Settings**: Adjustable smoothing, camera selection, and display options
- **🎨 Modern UI**: Clean, intuitive interface with real-time feedback
- **⚡ Fast Startup**: Optimized onedir executable for quick launching

## 📥 Download & Installation

### Quick Download (Recommended)
**📦 Download the ready-to-use executable:**

[**Ultimate Comfis Mouse - Latest Release v1.0.0 (google_drive)**](https://drive.google.com/drive/folders/1EKmxTCICWITWhYtkX5lMFDGBFFi9wMgN?usp=drive_link)

[**Ultimate Comfis Mouse - Latest Release v1.0.0 (github)**](https://github.com/yukakeren/interaksiku/releases/tag/v1.0.0)

1. Download the `interaksiku` folder from the link above
2. Extract to your desired location
3. Run `interaksiku.exe` inside the folder
4. That's it! No Python installation required.

### Developer Installation
If you want to run from source code:

```bash
# Clone the repository
git clone https://github.com/yukakeren/interaksiku.git
cd interaksiku

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 🚀 Quick Start Guide

### 1. **Launch the Application**
- Download and run `interaksiku.exe` from the link above
- The application will automatically detect available cameras

### 2. **Setup Your Camera**
- Click the 🔍 button to detect cameras
- Select your preferred camera from the dropdown
- Adjust display settings (mirror/flip) if needed

### 3. **Calibrate the Tracking Area**
- Switch to **📐 Calibration** mode
- Choose your calibration method:
  - **Manual**: Drag the colored corner points to define your tracking area
  - **OpenCV**: Follow on-screen instructions to place your hand at each corner
- Click **💾 Save Calibration** when satisfied

### 4. **Start Mouse Control**
- Switch to **🖱️ Mouse Control** mode
- Move your hand within the calibrated area to control the cursor
- **Make a fist** to click
- Adjust smoothing slider for comfortable movement speed

## 🎮 How to Use

### Mouse Control Gestures
| Gesture | Action |
|---------|--------|
| ✋ **Open Hand** | Move cursor |
| ✊ **Closed Fist** | Left click |
| 👆 **Point with Index** | Hover/Move only |

### Settings Options
- **📷 Camera Selection**: Choose from available cameras
- **🔄 Mirror Display**: Flip the video horizontally for natural interaction
- **📏 Calibration Method**: Manual drag-drop or automatic hand tracking
- **🎯 Mouse Smoothing**: Adjust from 1 (fast/jittery) to 10 (slow/smooth)

## 🛠️ Technical Architecture

This application features a clean, modular architecture:

### Core Components
- **`main.py`** - Application entry point
- **`ultimate_comfis_mouse_refactored.py`** - Main application controller
- **`ui_manager.py`** - User interface and layout management
- **`camera_manager.py`** - Camera detection and video capture
- **`hand_tracker.py`** - MediaPipe hand tracking integration
- **`calibration_manager.py`** - Calibration data and transformations
- **`mouse_controller.py`** - Mouse control and gesture recognition
- **`video_manager.py`** - Video display utilities
- **`config.py`** - Application configuration and constants

### Dependencies
- **MediaPipe** - Hand tracking and gesture recognition
- **OpenCV** - Computer vision and image processing
- **Tkinter** - User interface framework
- **PyAutoGUI** - Mouse control
- **Pynput** - Advanced input handling
- **Pillow** - Image processing for UI

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Camera Not Detected
- **Solution**: Ensure camera is connected and not used by other apps
- Try different USB ports for external cameras
- Check camera permissions in Windows settings

#### Hand Tracking Not Working
- **Solution**: Ensure good lighting conditions
- Keep your hand clearly visible to the camera
- Avoid cluttered backgrounds
- Make sure your hand is within the calibrated area

#### Cursor Movement Too Fast/Slow
- **Solution**: Adjust the "Mouse Smoothing" slider
- Higher values = smoother but slower movement
- Lower values = faster but more responsive movement

#### Application Won't Start
- **Solution**: 
  - Download the complete `interaksiku` folder (not just the .exe)
  - Ensure Windows Defender isn't blocking the application
  - Run as administrator if needed

#### Calibration Issues
- **Manual Method**: Drag corner points to cover your hand movement area
- **OpenCV Method**: Ensure good lighting and clear hand visibility
- **Tip**: Start with manual calibration - it's more reliable

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB
- **Storage**: 500MB free space
- **Camera**: Any USB webcam or built-in camera
- **CPU**: Intel i3 or equivalent

### Recommended
- **RAM**: 8GB or higher
- **Camera**: HD webcam (720p or higher)
- **CPU**: Intel i5 or equivalent
- **Lighting**: Good ambient lighting for hand tracking

## 🆘 Support & Community

- **📖 Documentation**: Check this README for detailed instructions
- **🐛 Bug Reports**: Open an issue on the GitHub repository
- **💡 Feature Requests**: Share your ideas via GitHub issues
- **📧 Direct Support**: Contact the developer for specific issues

## 📄 License

This project is open source and available under the MIT License. Feel free to modify, distribute, and use for both personal and commercial purposes.

## 🔮 Future Enhancements

- **Multi-Hand Support** - Track both hands simultaneously
- **Advanced Gestures** - Scroll, zoom, right-click with different gestures
- **Voice Commands** - Combine voice with hand gestures
- **Eye Tracking** - Additional input method for accessibility
- **Gaming Mode** - Optimized settings for gaming applications
- **Multi-Monitor** - Support for multiple display setups

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/your-username/interaksiku.git
cd interaksiku

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements_ultimate_comfis.txt

# Run from source
python main.py
```

---

**Made with ❤️ for the accessibility and gesture control community**

*Star ⭐ this repository if you found it helpful!*

## Improvements in Refactored Version

### Code Organization
- **Modular Design**: Separated concerns into focused modules
- **Single Responsibility**: Each class has a clear, single purpose
- **Loose Coupling**: Modules communicate through well-defined interfaces

### Maintainability
- **Configuration Management**: Centralized configuration in `config.py`
- **Error Handling**: Improved error handling and user feedback
- **Code Documentation**: Comprehensive docstrings and comments

### Extensibility
- **Plugin Architecture**: Easy to add new calibration methods or controllers
- **Configurable Parameters**: Settings can be easily modified
- **Interface Abstractions**: Well-defined interfaces for extending functionality

### Performance
- **Threaded Camera Operations**: Camera operations run in separate threads
- **Efficient Video Display**: Optimized video frame display
- **Resource Management**: Proper cleanup and resource management

### User Experience
- **Better UI Organization**: Cleaner, more intuitive interface
- **Improved Feedback**: Better status messages and error handling
- **Responsive Design**: Non-blocking UI operations

## Module Dependencies

```
main.py
└── ultimate_comfis_mouse_refactored.py
    ├── config.py
    ├── camera_manager.py
    ├── hand_tracker.py
    ├── calibration_manager.py
    ├── mouse_controller.py
    ├── ui_manager.py
    └── video_manager.py
```

## Configuration

Key settings can be modified in `config.py`:

- **UI Constants**: Colors, fonts, window sizes
- **Camera Settings**: Resolution, FPS, detection parameters
- **Hand Tracking**: Confidence thresholds, gesture parameters
- **Calibration**: Default points, canvas size, corner names

## Troubleshooting

### Camera Issues
- Ensure camera is connected and not used by other applications
- Try different camera indices if detection fails
- Check camera permissions

### Performance Issues
- Adjust smoothing factor for better performance
- Lower camera resolution if needed
- Ensure adequate lighting for hand tracking

### Calibration Problems
- Use manual calibration if OpenCV method fails
- Ensure good lighting for hand tracking calibration
- Recalibrate if cursor mapping seems off

## Development

### Adding New Features

1. **New Calibration Method**:
   - Extend `CalibrationManager` 
   - Add UI components in `ui_manager.py`
   - Update configuration in `config.py`

2. **New Controller**:
   - Create new controller module
   - Implement similar interface to `MouseController`
   - Integrate in main application

3. **UI Improvements**:
   - Modify `ui_manager.py`
   - Update styling in `config.py`
   - Add new content classes as needed

### Testing

The modular structure makes testing easier:
- Unit test individual modules
- Mock dependencies for isolated testing
- Test UI components separately from business logic

## License

This project is open source. Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing architecture
4. Test thoroughly
5. Submit a pull request

## Future Enhancements

- Multiple hand tracking
- Gesture-based actions (scroll, right-click, etc.)
- Voice commands integration
- Eye tracking support
- Multi-monitor support
- Custom gesture training
