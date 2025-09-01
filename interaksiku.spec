# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect MediaPipe data files
mediapipe_datas = collect_data_files('mediapipe')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('camera_manager.py', '.'),
        ('hand_tracker.py', '.'),
        ('calibration_manager.py', '.'),
        ('mouse_controller.py', '.'),
        ('ui_manager.py', '.'),
        ('video_manager.py', '.'),
        ('ultimate_comfis_mouse_refactored.py', '.'),
        ('icon.ico', '.'),  # Include icon file as data
    ] + mediapipe_datas,
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pynput',
        'pynput.mouse',
        'pynput.mouse._win32',
        'tkinter',
        'tkinter.ttk',
        'threading',
        'mediapipe',
        'pyautogui',
        'config',
        'camera_manager',
        'hand_tracker', 
        'calibration_manager',
        'mouse_controller',
        'ui_manager',
        'video_manager',
        'ultimate_comfis_mouse_refactored',
        'mediapipe.python.solutions.hands',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solution_base',
    ] + collect_submodules('mediapipe'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='interaksiku',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='interaksiku',
)
