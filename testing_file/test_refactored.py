# Simple test script for the refactored Ultimate Comfis Mouse
"""
Test script to verify the refactored modules work correctly.
This script tests basic functionality without requiring camera hardware.
"""

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing module imports...")
    
    try:
        import config
        print("✅ config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from camera_manager import CameraManager
        print("✅ CameraManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CameraManager: {e}")
        return False
    
    try:
        from hand_tracker import HandTracker, PositionSmoother
        print("✅ HandTracker modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import HandTracker: {e}")
        return False
    
    try:
        from calibration_manager import CalibrationManager, ManualCalibration
        print("✅ CalibrationManager modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CalibrationManager: {e}")
        return False
    
    try:
        from video_manager import VideoDisplayManager, CameraThread, FrameProcessor
        print("✅ VideoManager modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import VideoManager: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of core modules"""
    print("\nTesting basic functionality...")
    
    try:
        # Test CameraManager
        from camera_manager import CameraManager
        camera_manager = CameraManager()
        print(f"✅ CameraManager created, screen size: {camera_manager.screen_w}x{camera_manager.screen_h}")
    except Exception as e:
        print(f"❌ CameraManager test failed: {e}")
        return False
    
    try:
        # Test CalibrationManager
        from calibration_manager import CalibrationManager
        cal_manager = CalibrationManager(1920, 1080)
        
        # Test adding points
        cal_manager.add_calibration_point([100, 100])
        cal_manager.add_calibration_point([500, 100])
        cal_manager.add_calibration_point([500, 400])
        cal_manager.add_calibration_point([100, 400])
        
        if cal_manager.is_calibrated():
            print("✅ CalibrationManager test passed")
        else:
            print("❌ CalibrationManager calibration failed")
            return False
    except Exception as e:
        print(f"❌ CalibrationManager test failed: {e}")
        return False
    
    try:
        # Test PositionSmoother
        from hand_tracker import PositionSmoother
        smoother = PositionSmoother(5)
        
        # Add some positions
        pos1 = smoother.add_position(100, 100)
        pos2 = smoother.add_position(105, 102)
        pos3 = smoother.add_position(110, 104)
        
        print(f"✅ PositionSmoother test passed: {pos1} -> {pos2} -> {pos3}")
    except Exception as e:
        print(f"❌ PositionSmoother test failed: {e}")
        return False
    
    try:
        # Test ManualCalibration
        from calibration_manager import ManualCalibration
        manual_cal = ManualCalibration()
        
        # Test point manipulation
        closest = manual_cal.find_closest_point(100, 100)
        manual_cal.update_point(0, 150, 150)
        points = manual_cal.get_points()
        
        print(f"✅ ManualCalibration test passed, closest point: {closest}, points: {len(points)}")
    except Exception as e:
        print(f"❌ ManualCalibration test failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration values"""
    print("\nTesting configuration...")
    
    try:
        from config import COLORS, FONTS, CAMERA_SETTINGS, HAND_TRACKING, CALIBRATION
        
        # Check that required config sections exist
        required_colors = ['primary', 'secondary', 'success', 'danger', 'background', 'white', 'black']
        for color in required_colors:
            if color not in COLORS:
                print(f"❌ Missing color: {color}")
                return False
        
        required_fonts = ['title', 'subtitle', 'heading', 'normal', 'button']
        for font in required_fonts:
            if font not in FONTS:
                print(f"❌ Missing font: {font}")
                return False
        
        # Check camera settings
        if 'default_width' not in CAMERA_SETTINGS:
            print("❌ Missing camera default_width")
            return False
        
        print("✅ Configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Ultimate Comfis Mouse - Refactored Version Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Configuration", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored code is working correctly.")
        print("\nYou can now run the application with:")
        print("python main.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    main()
