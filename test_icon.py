#!/usr/bin/env python3
"""
Simple test script to verify icon loading works correctly
"""
import tkinter as tk
import sys
import os

def test_icon():
    """Test if icon can be loaded properly"""
    root = tk.Tk()
    root.title("Icon Test")
    root.geometry("300x200")
    
    try:
        if getattr(sys, 'frozen', False):  # Running as exe
            # Get the directory where the exe is located
            icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            print(f"Looking for icon at (exe): {icon_path}")
        else:  # Running as script
            icon_path = "icon.ico"
            print(f"Looking for icon at (script): {icon_path}")
        
        print(f"Icon file exists: {os.path.exists(icon_path)}")
        
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
            print("✅ Icon loaded successfully!")
            status_text = "✅ Icon loaded successfully!"
        else:
            print("❌ Icon file not found!")
            status_text = "❌ Icon file not found!"
            
    except Exception as e:
        print(f"❌ Error loading icon: {e}")
        status_text = f"❌ Error loading icon: {e}"
    
    # Show status in window
    label = tk.Label(
        root,
        text=status_text,
        font=("Arial", 12),
        justify="center"
    )
    label.pack(expand=True)
    
    # Close after 3 seconds
    root.after(3000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    test_icon()
