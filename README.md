# Ultimate Comfis Mouse - Refactored

A modular hand tracking mouse control application with calibration features. This refactored version improves code organization, maintainability, and extensibility.

## Features

- **Hand Tracking**: Uses MediaPipe for real-time hand detection and tracking
- **Mouse Control**: Control your cursor with hand gestures
- **Calibration**: Two calibration methods:
  - Manual: Drag and drop interface
  - OpenCV: Hand tracking-based calibration
- **Camera Support**: Automatic camera detection and selection
- **Smooth Movement**: Configurable mouse movement smoothing
- **Modern UI**: Clean, intuitive interface

## Refactored Architecture

The application has been restructured into modular components:

### Core Modules

#### `config.py`
- Configuration constants and settings
- UI colors, fonts, and layout constants
- Camera and hand tracking parameters
- File paths and environment setup

#### `camera_manager.py`
- Camera detection and initialization
- Camera configuration and management
- Support for multiple camera backends

#### `hand_tracker.py`
- Hand tracking using MediaPipe
- Gesture recognition (fist for clicking)
- Position smoothing utilities
- Hand landmark processing

#### `calibration_manager.py`
- Calibration data management
- Perspective transformation calculations
- Manual calibration utilities
- Save/load calibration data

#### `mouse_controller.py`
- Mouse control logic
- Integration with hand tracking
- Click detection and handling
- Calibration process control

#### `ui_manager.py`
- User interface components
- Layout management
- Event handling
- Content display for different modes

#### `video_manager.py`
- Video display utilities
- Frame processing base classes
- Camera thread management
- Video frame display in tkinter

#### `ultimate_comfis_mouse_refactored.py`
- Main application controller
- Coordinates all modules
- Application lifecycle management

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Quick Start

1. **Select Camera**: Choose your camera from the dropdown
2. **Calibration**: 
   - Go to Calibration mode
   - Choose manual or OpenCV method
   - Follow the instructions to set up tracking area
   - Save the calibration
3. **Mouse Control**:
   - Switch to Mouse Control mode
   - Move your hand to control the cursor
   - Make a fist to click

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
