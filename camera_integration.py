#!/usr/bin/env python3
"""
Standalone Camera Integration System
Simplified camera management without external dependencies
"""

import cv2
import subprocess
import os
import time
import threading
from datetime import datetime
from typing import Dict, Tuple, Optional, List

# Camera configuration
CAMERAS = {
    1: {
        'name': 'Overhead Camera',
        'node': '/dev/video0',
        'capture_resolution': (8000, 6000),
        'preview_resolution': (640, 480),
        'focus_value': 120,
        'rotate': True
    },
    2: {
        'name': 'Side Camera', 
        'node': '/dev/video2',
        'capture_resolution': (1920, 1080),
        'preview_resolution': (640, 480),
        'focus_value': 120,
        'rotate': False
    }
}

# Global state
camera_system_initialized = False
current_data_folder = "data"
gui_instance = None

def initialize_camera_system(data_folder: str = "data") -> bool:
    """
    Initialize the camera system
    
    Args:
        data_folder: Folder to save captured images
        
    Returns:
        bool: True if initialization successful
    """
    global camera_system_initialized, current_data_folder
    
    print("Initializing camera system...")
    
    # Set data folder
    current_data_folder = data_folder
    if not os.path.exists(current_data_folder):
        os.makedirs(current_data_folder)
        print(f"Created data folder: {current_data_folder}")
    
    # Check camera availability
    available_cameras = check_camera_availability()
    if available_cameras == 0:
        print("⚠️  No cameras available!")
        return False
    
    print(f"✓ Camera system initialized with {available_cameras} camera(s)")
    camera_system_initialized = True
    return True

def check_camera_availability() -> int:
    """Check which cameras are available and accessible"""
    available = 0
    
    for camera_id, config in CAMERAS.items():
        if os.path.exists(config['node']):
            if os.access(config['node'], os.R_OK | os.W_OK):
                print(f"✓ Camera {camera_id} ({config['name']}): {config['node']}")
                available += 1
            else:
                print(f"⚠️  Camera {camera_id}: No permission for {config['node']}")
        else:
            print(f"⚠️  Camera {camera_id}: {config['node']} not found")
    
    return available

def set_camera_focus(camera_id: int, focus_value: int) -> bool:
    """
    Set camera focus manually
    
    Args:
        camera_id: Camera ID (1 or 2)
        focus_value: Focus value (0-127)
        
    Returns:
        bool: True if successful
    """
    if camera_id not in CAMERAS:
        print(f"❌ Invalid camera ID: {camera_id}")
        return False
    
    config = CAMERAS[camera_id]
    device_node = config['node']
    
    try:
        # Set manual focus
        subprocess.run([
            "v4l2-ctl", "-d", device_node,
            "--set-ctrl=focus_automatic_continuous=0",
            f"--set-ctrl=focus_absolute={focus_value}"
        ], check=False, capture_output=True)
        
        print(f"✓ Camera {camera_id} focus set to {focus_value}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to set focus for camera {camera_id}: {e}")
        return False

def capture_image(camera_id: int, filename: Optional[str] = None, method: str = 'fswebcam') -> Tuple[bool, str]:
    """
    Capture image from specified camera
    
    Args:
        camera_id: Camera ID (1 or 2)
        filename: Output filename (auto-generated if None)
        method: Capture method ('fswebcam' or 'opencv')
        
    Returns:
        Tuple[bool, str]: (success, filename_or_error_message)
    """
    if camera_id not in CAMERAS:
        return False, f"Invalid camera ID: {camera_id}"
    
    config = CAMERAS[camera_id]
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"camera{camera_id}_{timestamp}.jpg"
    
    # Ensure filename has .jpg extension
    if not filename.endswith('.jpg'):
        filename += '.jpg'
    
    # Full path
    filepath = os.path.join(current_data_folder, filename)
    
    print(f"📸 Capturing from camera {camera_id} ({config['name']})...")
    
    if method.lower() == 'fswebcam':
        return _capture_fswebcam(camera_id, config, filepath)
    elif method.lower() == 'opencv':
        return _capture_opencv(camera_id, config, filepath)
    else:
        return False, f"Unknown capture method: {method}"

def _capture_fswebcam(camera_id: int, config: dict, filepath: str) -> Tuple[bool, str]:
    """Capture using fswebcam"""
    device_node = config['node']
    width, height = config['capture_resolution']
    rotate = config['rotate']
    
    try:
        # Build command
        cmd = [
            "fswebcam",
            "-d", device_node,
            "-r", f"{width}x{height}",
            "--jpeg", "95",
            "--no-banner",
            "--skip", "2",
            "-v",
            filepath
        ]
        
        if rotate:
            cmd.extend(["--rotate", "180"])
        
        # Execute capture
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / (1024*1024)  # MB
            print(f"✓ Image saved: {filepath} ({file_size:.1f} MB)")
            return True, filepath
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            return False, f"fswebcam failed: {error_msg}"
            
    except subprocess.TimeoutExpired:
        return False, "Capture timed out"
    except Exception as e:
        return False, f"Capture error: {str(e)}"

def _capture_opencv(camera_id: int, config: dict, filepath: str) -> Tuple[bool, str]:
    """Capture using OpenCV"""
    device_node = config['node']
    width, height = config['capture_resolution']
    rotate = config['rotate']
    
    # Extract device number
    device_num = int(device_node.split('video')[-1])
    
    try:
        # Open camera
        cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
        
        if not cap.isOpened():
            return False, f"Failed to open {device_node}"
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Allow camera to adjust
        time.sleep(1)
        
        # Capture frame
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            # Apply rotation if needed
            if rotate:
                frame = cv2.flip(frame, -1)  # 180 degree rotation
            
            # Save image
            success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if success:
                file_size = os.path.getsize(filepath) / (1024*1024)  # MB
                print(f"✓ Image saved: {filepath} ({file_size:.1f} MB)")
                return True, filepath
            else:
                return False, "Failed to save image"
        else:
            return False, "Failed to capture frame"
            
    except Exception as e:
        return False, f"OpenCV error: {str(e)}"

def capture_all_cameras(filename_prefix: str = "capture", method: str = 'fswebcam') -> Dict[int, Tuple[bool, str]]:
    """
    Capture from all available cameras
    
    Args:
        filename_prefix: Prefix for filenames
        method: Capture method
        
    Returns:
        Dict[int, Tuple[bool, str]]: Results for each camera
    """
    results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for camera_id in CAMERAS.keys():
        if os.path.exists(CAMERAS[camera_id]['node']):
            filename = f"{filename_prefix}_camera{camera_id}_{timestamp}.jpg"
            success, result = capture_image(camera_id, filename, method)
            results[camera_id] = (success, result)
        else:
            results[camera_id] = (False, f"Camera {camera_id} not available")
    
    return results

def list_cameras() -> List[Dict]:
    """List available cameras"""
    cameras = []
    
    for camera_id, config in CAMERAS.items():
        available = os.path.exists(config['node']) and os.access(config['node'], os.R_OK | os.W_OK)
        
        cameras.append({
            'id': camera_id,
            'name': config['name'],
            'node': config['node'],
            'available': available,
            'capture_resolution': config['capture_resolution'],
            'preview_resolution': config['preview_resolution']
        })
    
    return cameras

def get_camera_info(camera_id: int) -> Optional[Dict]:
    """Get information about a specific camera"""
    if camera_id not in CAMERAS:
        return None
    
    config = CAMERAS[camera_id]
    available = os.path.exists(config['node']) and os.access(config['node'], os.R_OK | os.W_OK)
    
    return {
        'id': camera_id,
        'name': config['name'],
        'node': config['node'],
        'available': available,
        'capture_resolution': config['capture_resolution'],
        'preview_resolution': config['preview_resolution'],
        'focus_value': config['focus_value'],
        'rotate': config['rotate']
    }

def check_dependencies() -> bool:
    """Check if required tools are available"""
    dependencies_ok = True
    
    # Check fswebcam
    try:
        subprocess.run(["fswebcam", "--version"], capture_output=True, check=True)
        print("✓ fswebcam available")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  fswebcam not found. Install with: sudo apt install fswebcam")
        dependencies_ok = False
    
    # Check v4l2-ctl
    try:
        subprocess.run(["v4l2-ctl", "--version"], capture_output=True, check=True)
        print("✓ v4l2-ctl available")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  v4l2-ctl not found. Install with: sudo apt install v4l-utils")
        dependencies_ok = False
    
    # Check OpenCV
    try:
        cv2_version = cv2.__version__
        print(f"✓ OpenCV available (version {cv2_version})")
    except:
        print("⚠️  OpenCV not available")
        dependencies_ok = False
    
    return dependencies_ok

def set_gui_instance(gui):
    """Set GUI instance for preview management (optional)"""
    global gui_instance
    gui_instance = gui

def get_data_folder() -> str:
    """Get current data folder"""
    return current_data_folder

def set_data_folder(folder: str):
    """Set data folder for captures"""
    global current_data_folder
    current_data_folder = folder
    if not os.path.exists(current_data_folder):
        os.makedirs(current_data_folder)
        print(f"Created data folder: {current_data_folder}")

# Initialize on import
if __name__ == "__main__":
    print("Camera Integration System")
    print("=" * 30)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check camera availability
    available = check_camera_availability()
    
    print(f"\nSystem Status:")
    print(f"  Dependencies: {'✓ OK' if deps_ok else '❌ Missing'}")
    print(f"  Cameras: {available} available")
    
    if available > 0:
        print("\nAvailable cameras:")
        for camera in list_cameras():
            status = "✓ Available" if camera['available'] else "❌ Not available"
            print(f"  Camera {camera['id']}: {camera['name']} - {status}") 