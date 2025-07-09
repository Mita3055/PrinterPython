#!/usr/bin/env python3
"""
Test script for the Printer GUI with Multi-Camera Preview
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_printer_gui():
    """Test the printer GUI"""
    try:
        from Camera_gui import main
        print("Starting Printer GUI with Multi-Camera Preview...")
        print("Features:")
        print("  - Live camera previews in one window")
        print("  - Preview switching during captures (like camera GUI)")
        print("  - Printer control interface (expandable)")
        print("  - Settings for data folder and capture method")
        print("  - Focus control for supported cameras")
        print()
        print("Press Ctrl+C to exit")
        
        main()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all required modules are available:")
        print("  - Camera/camera_manager.py")
        print("  - camera_integration.py")
        print("  - Required packages: tkinter, PIL, opencv-python")
    except Exception as e:
        print(f"Error starting GUI: {e}")

if __name__ == "__main__":
    test_printer_gui() 