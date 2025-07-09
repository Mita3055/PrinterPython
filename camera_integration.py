#!/usr/bin/env python3
"""
<<<<<<< HEAD
Camera Operations Module
Core camera functionality for multi-camera systems
Designed for integration with automated printer systems
=======
Standalone Camera Integration System
Simplified camera management without external dependencies
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
"""

import cv2
import subprocess
<<<<<<< HEAD
import threading
import time
import os
from datetime import datetime
from typing import Dict, Tuple, Optional, List

# Camera Configuration
VIDEO_DEVICES = {
    'video0': {
        'node': '/dev/video0',
        'capture_resolution': (8000, 6000),
        'preview_resolution': (640, 480),
        'focus_value': 120,  # Manual focus start value
        'rotate': True,
        'name': 'Camera_0'
    },
    'video2': {
        'node': '/dev/video2',
        'capture_resolution': (1920, 1080),
        'preview_resolution': (640, 480),
        'focus_value': None,  # Auto focus
        'rotate': False,
        'name': 'Camera_2'
    }
}

# Preview settings
PREVIEW_FOURCC = cv2.VideoWriter_fourcc(*'YUYV')
PREVIEW_FPS = 20
FOCUS_MIN, FOCUS_MAX = 1, 127

# Global state for camera system
_camera_streams = {}
_timelapse_workers = {}

def check_dependencies() -> bool:
    """Check if required camera tools are available"""
    dependencies_ok = True
    
    try:
        subprocess.run(["fswebcam", "--version"], capture_output=True, text=True, check=True)
        print("[+] fswebcam found")
    except FileNotFoundError:
        print("[!] fswebcam not found. Install: sudo apt install fswebcam")
        dependencies_ok = False
    
    try:
        subprocess.run(["v4l2-ctl", "--version"], capture_output=True, check=True)
        print("[+] v4l2-ctl found")
    except:
        print("[!] v4l2-ctl not found. Install: sudo apt install v4l-utils")
        dependencies_ok = False
    
    return dependencies_ok

def get_available_cameras() -> List[str]:
    """Get list of available camera device IDs"""
    available = []
    for device_id, config in VIDEO_DEVICES.items():
        if os.path.exists(config['node']) and os.access(config['node'], os.R_OK | os.W_OK):
            available.append(device_id)
        else:
            print(f"[!] Cannot access {config['node']}")
    return available

def set_camera_focus(device_node: str, focus_value: Optional[int] = None) -> bool:
    """
    Set camera focus - manual if value provided, auto if None
    
    Args:
        device_node: Camera device path (e.g., '/dev/video0')
        focus_value: Focus value (1-127) or None for auto focus
=======
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
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
        
    Returns:
        bool: True if successful
    """
<<<<<<< HEAD
    try:
        if focus_value is not None:
            # Manual focus
            subprocess.run([
                "v4l2-ctl", "-d", device_node,
                "--set-ctrl=focus_automatic_continuous=0",
                f"--set-ctrl=focus_absolute={focus_value}"
            ], check=False)
            print(f"[*] {device_node}: Manual focus set to {focus_value}")
        else:
            # Auto focus
            subprocess.run([
                "v4l2-ctl", "-d", device_node,
                "--set-ctrl=focus_automatic_continuous=1"
            ], check=False)
            print(f"[*] {device_node}: Auto focus enabled")
        return True
    except Exception as e:
        print(f"[!] Failed to set focus for {device_node}: {e}")
        return False

def initialize_cameras() -> bool:
    """
    Initialize all available cameras with their focus settings
    
    Returns:
        bool: True if at least one camera was initialized
    """
    available_cameras = get_available_cameras()
    
    if not available_cameras:
        print("[!] No cameras available for initialization")
        return False
    
    for device_id in available_cameras:
        config = VIDEO_DEVICES[device_id]
        set_camera_focus(config['node'], config['focus_value'])
        print(f"[+] Initialized camera {device_id} ({config['name']})")
    
    return True

def capture_image_fswebcam(device_id: str, save_path: Optional[str] = None, 
                          filename: Optional[str] = None) -> Tuple[bool, str]:
    """
    Capture high-resolution image using fswebcam
    
    Args:
        device_id: Camera device ID (e.g., 'video0')
        save_path: Directory to save image (current dir if None)
        filename: Custom filename (auto-generated if None)
=======
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
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
        
    Returns:
        Tuple[bool, str]: (success, filename_or_error_message)
    """
<<<<<<< HEAD
    if device_id not in VIDEO_DEVICES:
        return False, f"Unknown device ID: {device_id}"
    
    config = VIDEO_DEVICES[device_id]
    device_node = config['node']
    width, height = config['capture_resolution']
    camera_name = config['name']
    rotate = config['rotate']
=======
    if camera_id not in CAMERAS:
        return False, f"Invalid camera ID: {camera_id}"
    
    config = CAMERAS[camera_id]
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
<<<<<<< HEAD
        filename = f"{camera_name}_{timestamp}.jpg"
    
    # Set save path
    if save_path:
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        filepath = os.path.join(save_path, filename)
    else:
        filepath = filename
    
    print(f"[*] Capturing from {device_node} ({width}x{height})...")
    
    # Stop preview stream if active
    _stop_preview_stream(device_id)
    
    try:
=======
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
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
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
        
<<<<<<< HEAD
        print(f"[*] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024*1024)
            print(f"[+] Photo saved: {os.path.abspath(filepath)} ({size_mb:.1f} MB)")
            return True, filepath
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            print(f"[!] fswebcam failed for {device_node}: {error_msg}")
            return False, f"fswebcam error: {error_msg}"
            
    except subprocess.TimeoutExpired:
        print(f"[!] fswebcam timed out for {device_node}")
        return False, "Capture timed out"
    except Exception as e:
        print(f"[!] fswebcam exception for {device_node}: {e}")
        return False, str(e)
    finally:
        # Restart preview stream if it was active
        _restart_preview_stream(device_id)

def capture_image_opencv(device_id: str, save_path: Optional[str] = None,
                        filename: Optional[str] = None) -> Tuple[bool, str]:
    """
    Capture image using OpenCV (fallback method)
    
    Args:
        device_id: Camera device ID
        save_path: Directory to save image
        filename: Custom filename
        
    Returns:
        Tuple[bool, str]: (success, filename_or_error_message)
    """
    if device_id not in VIDEO_DEVICES:
        return False, f"Unknown device ID: {device_id}"
    
    config = VIDEO_DEVICES[device_id]
    device_node = config['node']
    width, height = config['capture_resolution']
    camera_name = config['name']
    rotate = config['rotate']
    device_num = int(device_node.split('video')[-1])
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{camera_name}_{timestamp}_opencv.jpg"
    
    # Set save path
    if save_path:
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        filepath = os.path.join(save_path, filename)
    else:
        filepath = filename
    
    print(f"[*] OpenCV capture from {device_node} ({width}x{height})...")
    
    # Stop preview stream if active
    _stop_preview_stream(device_id)
    
    try:
        cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
        if not cap.isOpened():
            return False, f"Failed to open {device_node}"
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        time.sleep(1)  # Allow camera to adjust
        
=======
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
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
<<<<<<< HEAD
            if rotate:
                frame = cv2.flip(frame, -1)
            
            success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if success:
                size_mb = os.path.getsize(filepath) / (1024*1024)
                print(f"[+] Photo saved: {os.path.abspath(filepath)} ({size_mb:.1f} MB)")
=======
            # Apply rotation if needed
            if rotate:
                frame = cv2.flip(frame, -1)  # 180 degree rotation
            
            # Save image
            success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if success:
                file_size = os.path.getsize(filepath) / (1024*1024)  # MB
                print(f"✓ Image saved: {filepath} ({file_size:.1f} MB)")
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
                return True, filepath
            else:
                return False, "Failed to save image"
        else:
            return False, "Failed to capture frame"
            
    except Exception as e:
<<<<<<< HEAD
        return False, str(e)
    finally:
        # Restart preview stream if it was active
        _restart_preview_stream(device_id)

def capture_image(device_id: str, save_path: Optional[str] = None,
                 filename: Optional[str] = None, method: str = 'fswebcam') -> Tuple[bool, str]:
    """
    Capture image with automatic fallback between methods
    
    Args:
        device_id: Camera device ID
        save_path: Directory to save image
        filename: Custom filename
        method: Primary method ('fswebcam' or 'opencv')
        
    Returns:
        Tuple[bool, str]: (success, filename_or_error_message)
    """
    if method.lower() == 'fswebcam':
        success, result = capture_image_fswebcam(device_id, save_path, filename)
        if not success:
            print(f"[*] fswebcam failed, trying OpenCV fallback...")
            success, result = capture_image_opencv(device_id, save_path, filename)
    else:
        success, result = capture_image_opencv(device_id, save_path, filename)
        if not success:
            print(f"[*] OpenCV failed, trying fswebcam fallback...")
            success, result = capture_image_fswebcam(device_id, save_path, filename)
    
    return success, result

def capture_all_cameras(save_path: Optional[str] = None, 
                       filename_prefix: str = "capture") -> Dict[str, Tuple[bool, str]]:
    """
    Capture images from all available cameras simultaneously
    
    Args:
        save_path: Directory to save images
        filename_prefix: Prefix for filenames
        
    Returns:
        Dict[str, Tuple[bool, str]]: Results for each camera
    """
    available_cameras = get_available_cameras()
    results = {}
    
    if not available_cameras:
        print("[!] No cameras available for capture")
        return results
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Capture from each camera
    for device_id in available_cameras:
        config = VIDEO_DEVICES[device_id]
        filename = f"{filename_prefix}_{config['name']}_{timestamp}.jpg"
        
        success, result = capture_image(device_id, save_path, filename)
        results[device_id] = (success, result)
        
        if success:
            print(f"[+] {device_id} captured successfully")
        else:
            print(f"[!] {device_id} capture failed: {result}")
    
    return results

def start_timelapse(device_id: str, interval_seconds: float, duration_seconds: float,
                   save_path: str, filename_prefix: str = "timelapse") -> bool:
    """
    Start timelapse capture for a specific camera
    
    Args:
        device_id: Camera device ID
        interval_seconds: Time between captures
        duration_seconds: Total timelapse duration
        save_path: Directory to save timelapse images
        filename_prefix: Prefix for timelapse filenames
        
    Returns:
        bool: True if timelapse started successfully
    """
    if device_id not in VIDEO_DEVICES:
        print(f"[!] Unknown device ID: {device_id}")
        return False
    
    if device_id in _timelapse_workers:
        print(f"[!] Timelapse already running for {device_id}")
        return False
    
    # Create timelapse directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config = VIDEO_DEVICES[device_id]
    timelapse_dir = os.path.join(save_path, f"timelapse_{config['name']}_{timestamp}")
    os.makedirs(timelapse_dir, exist_ok=True)
    
    print(f"[+] Starting timelapse for {device_id}: {duration_seconds}s duration, {interval_seconds}s intervals")
    
    # Start timelapse worker thread
    worker = TimelapseWorker(device_id, interval_seconds, duration_seconds, 
                           timelapse_dir, filename_prefix)
    worker.start()
    _timelapse_workers[device_id] = worker
    
    return True

def stop_timelapse(device_id: str) -> bool:
    """
    Stop timelapse capture for a specific camera
    
    Args:
        device_id: Camera device ID
        
    Returns:
        bool: True if timelapse was stopped
    """
    if device_id in _timelapse_workers:
        _timelapse_workers[device_id].stop()
        del _timelapse_workers[device_id]
        print(f"[+] Stopped timelapse for {device_id}")
        return True
    else:
        print(f"[!] No timelapse running for {device_id}")
        return False

def is_timelapse_active(device_id: str) -> bool:
    """Check if timelapse is active for a camera"""
    return device_id in _timelapse_workers and _timelapse_workers[device_id].is_running()

# Preview stream management (for GUI integration)
class VideoStream:
    """Video stream for live preview"""
    
    def __init__(self, device_config):
        self.device_id = None
        for did, cfg in VIDEO_DEVICES.items():
            if cfg == device_config:
                self.device_id = did
                break
        
        self.node = device_config['node']
        self.w, self.h = device_config['preview_resolution']
        self.rotate = device_config['rotate']
        self.device_num = int(self.node.split('video')[-1])
        self.cap = None
        self.frame = None
        self.running = False

    def start(self) -> bool:
        """Start the video stream"""
        try:
            self.cap = cv2.VideoCapture(self.device_num, cv2.CAP_V4L2)
            if not self.cap.isOpened():
                return False
                
            self.cap.set(cv2.CAP_PROP_FOURCC, PREVIEW_FOURCC)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
            self.cap.set(cv2.CAP_PROP_FPS, PREVIEW_FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            self.running = True
            threading.Thread(target=self._reader, daemon=True).start()
            
            # Register stream globally
            if self.device_id:
                _camera_streams[self.device_id] = self
            
            return True
        except Exception as e:
            print(f"[!] Failed to start video stream: {e}")
            return False

    def _reader(self):
        """Background thread to read frames"""
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    if self.rotate:
                        frame = cv2.flip(frame, -1)
                    self.frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def stop(self):
        """Stop the video stream"""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Unregister stream globally
        if self.device_id and self.device_id in _camera_streams:
            del _camera_streams[self.device_id]

    def is_running(self) -> bool:
        """Check if stream is running"""
        return self.running

class TimelapseWorker:
    """Worker thread for timelapse capture"""
    
    def __init__(self, device_id: str, interval: float, duration: float, 
                 save_path: str, filename_prefix: str):
        self.device_id = device_id
        self.interval = interval
        self.duration = duration
        self.save_path = save_path
        self.filename_prefix = filename_prefix
        self.running = False
        self.thread = None

    def start(self):
        """Start the timelapse worker"""
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the timelapse worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def is_running(self) -> bool:
        """Check if worker is running"""
        return self.running

    def _worker(self):
        """Main timelapse worker function"""
        start_time = time.time()
        frame_count = 0
        
        print(f"[+] Timelapse worker started for {self.device_id}")
        
        while self.running and (time.time() - start_time) < self.duration:
            # Calculate when this frame should be captured
            target_time = start_time + (frame_count * self.interval)
            current_time = time.time()
            
            # Wait until it's time for next capture
            if current_time < target_time:
                sleep_time = target_time - current_time
                time.sleep(sleep_time)
            
            # Capture frame
            filename = f"{self.filename_prefix}_frame_{frame_count:04d}.jpg"
            success, result = capture_image(self.device_id, self.save_path, filename)
            
            if success:
                frame_count += 1
                elapsed = time.time() - start_time
                remaining = self.duration - elapsed
                print(f"[+] Timelapse {self.device_id}: Frame {frame_count} captured ({remaining:.0f}s remaining)")
            else:
                print(f"[!] Timelapse {self.device_id}: Frame {frame_count} failed - {result}")
            
            frame_count += 1
        
        print(f"[+] Timelapse completed for {self.device_id}: {frame_count} frames captured")
        self.running = False

# Internal helper functions
def _stop_preview_stream(device_id: str):
    """Stop preview stream for device (internal use)"""
    if device_id in _camera_streams:
        _camera_streams[device_id].stop()
        time.sleep(0.5)  # Allow device to be released

def _restart_preview_stream(device_id: str):
    """Restart preview stream for device (internal use)"""
    if device_id in VIDEO_DEVICES:
        config = VIDEO_DEVICES[device_id]
        stream = VideoStream(config)
        if stream.start():
            time.sleep(0.3)
            print(f"[+] Preview restarted for {device_id}")
        else:
            print(f"[!] Failed to restart preview for {device_id}")

def start_preview_stream(device_id: str) -> bool:
    """Start preview stream for a camera (public function)"""
    if device_id not in VIDEO_DEVICES:
        return False
    
    if device_id in _camera_streams:
        print(f"[!] Preview already running for {device_id}")
        return True
    
    config = VIDEO_DEVICES[device_id]
    stream = VideoStream(config)
    return stream.start()

def stop_preview_stream(device_id: str) -> bool:
    """Stop preview stream for a camera (public function)"""
    if device_id in _camera_streams:
        _camera_streams[device_id].stop()
        return True
    return False

def get_preview_frame(device_id: str):
    """Get current preview frame for a camera"""
    if device_id in _camera_streams:
        return _camera_streams[device_id].frame
    return None

# Cleanup function
def cleanup_all():
    """Stop all streams and workers"""
    # Stop all timelapse workers
    for device_id in list(_timelapse_workers.keys()):
        stop_timelapse(device_id)
    
    # Stop all preview streams
    for device_id in list(_camera_streams.keys()):
        stop_preview_stream(device_id)
    
    print("[+] Camera system cleanup completed")
=======
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
>>>>>>> a9be28b2acf9ed6e6f396b2cec409100c37576c0
