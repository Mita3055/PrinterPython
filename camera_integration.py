#!/usr/bin/env python3
"""
Camera Integration Module
Bridges the multi-camera GUI system with the main printing workflow
"""

import os
import sys
import time
from datetime import datetime
from Camera.camera_manager import (
    VIDEO_DEVICES, 
    capture_still_fswebcam, 
    capture_still_opencv,
    set_camera_focus,
    check_dependencies,
    check_camera_permissions
)

class CameraIntegration:
    """
    Integration class that provides capture commands for main.py
    while utilizing the advanced multi-camera system
    """
    
    def __init__(self, data_folder=None):
        self.data_folder = data_folder or "data"
        self.app_instance = None  # Will be set if GUI is running
        self.initialized = False
        
    def initialize(self):
        """Initialize the camera system"""
        print("Initializing multi-camera system...")
        
        # Check dependencies
        if not check_dependencies():
            print("Warning: Some camera dependencies missing")
        
        # Check camera permissions
        if not check_camera_permissions():
            print("Warning: Camera permission issues detected")
        
        # Set focus for cameras that support it
        for device_id, config in VIDEO_DEVICES.items():
            if config.get('focus_value') is not None:
                set_camera_focus(config['node'], config['focus_value'])
        
        self.initialized = True
        print("Multi-camera system initialized")
        return True
    
    def set_data_folder(self, folder_path):
        """Set the data folder for saving captures"""
        self.data_folder = folder_path
        os.makedirs(folder_path, exist_ok=True)
        print(f"Camera data folder set to: {folder_path}")
    
    def capture_image(self, camera_id, filename=None, method='fswebcam'):
        """
        Capture an image from the specified camera
        
        Args:
            camera_id: Camera identifier (1, 2, etc. or 'video0', 'video2')
            filename: Optional filename, will generate timestamped name if None
            method: 'fswebcam' or 'opencv'
        
        Returns:
            tuple: (success: bool, filename: str or error_message: str)
        """
        if not self.initialized:
            print("Camera system not initialized")
            return (False, "Camera system not initialized")
        
        # Map camera_id to device configuration
        device_config = self._get_device_config(camera_id)
        if not device_config:
            return (False, f"Camera {camera_id} not found")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            camera_name = device_config['name'].replace(' ', '_')
            filename = f"{camera_name}_{timestamp}.jpg"
        
        # Ensure filename is in data folder
        if not os.path.isabs(filename):
            filename = os.path.join(self.data_folder, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        print(f"Capturing image from {device_config['name']}...")
        
        # Choose capture method
        if method.lower() == 'fswebcam':
            success, result = capture_still_fswebcam(device_config, self.app_instance)
        elif method.lower() == 'opencv':
            success, result = capture_still_opencv(device_config, self.app_instance)
        else:
            return (False, f"Unknown capture method: {method}")
        
        if success:
            # Move file to desired location if it was saved elsewhere
            if result != filename and os.path.exists(result):
                import shutil
                shutil.move(result, filename)
                result = filename
            
            print(f"✓ Image captured: {filename}")
            return (True, filename)
        else:
            print(f"✗ Capture failed: {result}")
            return (False, result)
    
    def set_gui_instance(self, gui_instance):
        """Set the GUI instance for preview management during captures"""
        self.app_instance = gui_instance
    
    def capture_all_cameras(self, filename_prefix=None, method='fswebcam'):
        """
        Capture images from all available cameras
        
        Args:
            filename_prefix: Optional prefix for filenames
            method: 'fswebcam' or 'opencv'
        
        Returns:
            dict: {camera_id: (success, filename_or_error)}
        """
        results = {}
        
        for device_id, config in VIDEO_DEVICES.items():
            camera_name = config['name'].replace(' ', '_')
            if filename_prefix:
                filename = f"{filename_prefix}_{camera_name}.jpg"
            else:
                filename = None
            
            success, result = self.capture_image(device_id, filename, method)
            results[device_id] = (success, result)
        
        return results
    
    def set_camera_focus(self, camera_id, focus_value):
        """
        Set focus for a specific camera
        
        Args:
            camera_id: Camera identifier
            focus_value: Focus value (0-127) or None for auto focus
        """
        device_config = self._get_device_config(camera_id)
        if device_config:
            set_camera_focus(device_config['node'], focus_value)
            return True
        else:
            print(f"Camera {camera_id} not found")
            return False
    
    def get_camera_info(self, camera_id):
        """Get information about a specific camera"""
        device_config = self._get_device_config(camera_id)
        if device_config:
            return {
                'name': device_config['name'],
                'node': device_config['node'],
                'capture_resolution': device_config['capture_resolution'],
                'preview_resolution': device_config['preview_resolution'],
                'focus_value': device_config.get('focus_value'),
                'rotate': device_config.get('rotate', False)
            }
        return None
    
    def list_cameras(self):
        """List all available cameras"""
        cameras = []
        for device_id, config in VIDEO_DEVICES.items():
            cameras.append({
                'id': device_id,
                'name': config['name'],
                'node': config['node'],
                'capture_resolution': config['capture_resolution']
            })
        return cameras
    
    def _get_device_config(self, camera_id):
        """Get device configuration for camera_id"""
        # Handle numeric camera IDs (1, 2, etc.)
        if isinstance(camera_id, int):
            # Map to video devices (assuming camera 1 = video0, camera 2 = video2, etc.)
            if camera_id == 1:
                return VIDEO_DEVICES.get('video0')
            elif camera_id == 2:
                return VIDEO_DEVICES.get('video2')
            else:
                return None
        
        # Handle string camera IDs (video0, video2, etc.)
        return VIDEO_DEVICES.get(camera_id)

# Global instance for easy access
camera_integration = CameraIntegration()

# Convenience functions for main.py
def initialize_camera_system(data_folder=None):
    """Initialize the camera integration system"""
    global camera_integration
    if data_folder:
        camera_integration.set_data_folder(data_folder)
    return camera_integration.initialize()

def capture_image(camera_id, filename=None, method='fswebcam'):
    """Capture image from specified camera"""
    return camera_integration.capture_image(camera_id, filename, method)

def capture_all_cameras(filename_prefix=None, method='fswebcam'):
    """Capture from all cameras"""
    return camera_integration.capture_all_cameras(filename_prefix, method)

def set_camera_focus(camera_id, focus_value):
    """Set camera focus"""
    return camera_integration.set_camera_focus(camera_id, focus_value)

def get_camera_info(camera_id):
    """Get camera information"""
    return camera_integration.get_camera_info(camera_id)

def list_cameras():
    """List all available cameras"""
    return camera_integration.list_cameras() 