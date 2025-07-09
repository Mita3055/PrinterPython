#!/usr/bin/env python3
"""
Test script for the camera integration system
Demonstrates how to use the multi-camera capture functionality
"""

import os
import time
from datetime import datetime
from camera_integration import (
    initialize_camera_system,
    capture_image,
    capture_all_cameras,
    list_cameras,
    get_camera_info,
    set_camera_focus
)

def test_camera_integration():
    """Test the camera integration system"""
    
    print("=== Camera Integration Test ===\n")
    
    # Create test data folder
    test_folder = f"test_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(test_folder, exist_ok=True)
    
    # Initialize camera system
    print("1. Initializing camera system...")
    if not initialize_camera_system(test_folder):
        print("❌ Camera system initialization failed")
        return
    
    print("✅ Camera system initialized successfully\n")
    
    # List available cameras
    print("2. Available cameras:")
    cameras = list_cameras()
    for camera in cameras:
        print(f"   - {camera['name']} (ID: {camera['id']}) at {camera['node']}")
    print()
    
    # Test individual camera captures
    print("3. Testing individual camera captures...")
    for camera in cameras:
        camera_id = camera['id']
        camera_name = camera['name']
        
        print(f"   Capturing from {camera_name}...")
        success, result = capture_image(
            camera_id=camera_id,
            filename=f"test_{camera_name.lower().replace(' ', '_')}.jpg",
            method='fswebcam'
        )
        
        if success:
            print(f"   ✅ {camera_name}: {result}")
        else:
            print(f"   ❌ {camera_name}: {result}")
    
    print()
    
    # Test camera information
    print("4. Camera information:")
    for camera in cameras:
        camera_id = camera['id']
        info = get_camera_info(camera_id)
        if info:
            print(f"   {info['name']}:")
            print(f"     - Resolution: {info['capture_resolution']}")
            print(f"     - Focus: {info['focus_value']}")
            print(f"     - Rotate: {info['rotate']}")
    print()
    
    # Test capturing from all cameras at once
    print("5. Testing capture from all cameras...")
    all_results = capture_all_cameras(filename_prefix="all_cameras", method='fswebcam')
    
    for camera_id, (success, result) in all_results.items():
        if success:
            print(f"   ✅ Camera {camera_id}: {result}")
        else:
            print(f"   ❌ Camera {camera_id}: {result}")
    
    print()
    print("=== Test completed ===")
    print(f"Check the '{test_folder}' directory for captured images")

if __name__ == "__main__":
    test_camera_integration() 