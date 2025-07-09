# Camera Integration System

This document explains how to use the new camera integration system that bridges the multi-camera GUI with the main printing workflow.

## Overview

The camera integration system provides high-quality image capture capabilities from your multi-camera setup, integrated directly into your main printing workflow. It uses the advanced capture functions from the `Camera/camera_manager.py` system while providing a simple interface for `main.py`.

## Features

- **High-resolution captures**: Uses `fswebcam` for maximum quality (8000x6000 for overhead camera)
- **Multiple capture methods**: Support for both `fswebcam` and `opencv` capture methods
- **Automatic file management**: Organizes captures in timestamped data folders
- **Focus control**: Automatic focus setting for supported cameras
- **Error handling**: Robust error handling with detailed feedback

## Quick Start

### 1. Basic Usage in main.py

```python
from camera_integration import initialize_camera_system, capture_image

# Initialize the system
data_folder = "data/your_print_session"
initialize_camera_system(data_folder)

# Capture from a specific camera
success, filename = capture_image(
    camera_id=1,  # Camera 1 (Overhead Camera)
    filename="my_capture.jpg",
    method='fswebcam'
)

if success:
    print(f"Image saved: {filename}")
else:
    print(f"Capture failed: {filename}")  # filename contains error message
```

### 2. Capture During Print Sequence

The system is already integrated into `main.py`. When the toolpath contains capture commands like:

```gcode
;CAPTURE: 1, 17.5, 0, 60
```

The system will:
1. Move the print head to the specified position
2. Capture a high-resolution image from the specified camera
3. Save it with a descriptive filename including position and timestamp

### 3. Test the System

Run the test script to verify everything works:

```bash
python camera_test.py
```

## Camera Configuration

The system uses the camera configuration from `Camera/camera_manager.py`:

### Available Cameras

- **Camera 1 (video0)**: Overhead Camera
  - Capture resolution: 8000x6000
  - Preview resolution: 640x480
  - Focus: Auto (120)
  - Rotation: 180°

- **Camera 2 (video2)**: Side Camera
  - Capture resolution: 1920x1080
  - Preview resolution: 640x480
  - Focus: Manual (120)
  - Rotation: None

## API Reference

### Core Functions

#### `initialize_camera_system(data_folder=None)`
Initialize the camera integration system.

**Parameters:**
- `data_folder`: Optional path for saving captures

**Returns:** `bool` - True if initialization successful

#### `capture_image(camera_id, filename=None, method='fswebcam')`
Capture an image from a specific camera.

**Parameters:**
- `camera_id`: Camera identifier (1, 2, or 'video0', 'video2')
- `filename`: Optional filename (auto-generated if None)
- `method`: 'fswebcam' or 'opencv'

**Returns:** `tuple` - (success: bool, filename_or_error: str)

#### `capture_all_cameras(filename_prefix=None, method='fswebcam')`
Capture from all available cameras.

**Parameters:**
- `filename_prefix`: Optional prefix for filenames
- `method`: 'fswebcam' or 'opencv'

**Returns:** `dict` - {camera_id: (success, filename_or_error)}

#### `list_cameras()`
Get list of all available cameras.

**Returns:** `list` - List of camera dictionaries

#### `get_camera_info(camera_id)`
Get detailed information about a camera.

**Returns:** `dict` - Camera information or None

#### `set_camera_focus(camera_id, focus_value)`
Set focus for a camera.

**Parameters:**
- `camera_id`: Camera identifier
- `focus_value`: Focus value (0-127) or None for auto

**Returns:** `bool` - True if successful

## File Naming Convention

Captured images are automatically named with the following pattern:

```
{camera_name}_{timestamp}.jpg
```

For captures during printing:
```
camera{camera_id}_pos_{x}_{y}_{z}_{timestamp}.jpg
```

For final captures:
```
final_{camera_name}.jpg
```

## Integration with GUI

The camera integration system can work alongside the GUI system:

1. **GUI Mode**: Run `Camera/gui.py` for interactive camera control
2. **Programmatic Mode**: Use the integration functions in `main.py`
3. **Hybrid Mode**: Both can run simultaneously (GUI for monitoring, integration for automated captures)

## Troubleshooting

### Common Issues

1. **Camera not found**
   - Check if cameras are connected
   - Verify camera permissions: `sudo chmod 666 /dev/video*`
   - Run `ls /dev/video*` to list available devices

2. **fswebcam not found**
   - Install: `sudo apt install fswebcam`

3. **v4l2-ctl not found**
   - Install: `sudo apt install v4l-utils`

4. **Permission denied**
   - Add user to video group: `sudo usermod -a -G video $USER`
   - Log out and back in

### Debug Mode

Enable debug output by setting the environment variable:
```bash
export CAMERA_DEBUG=1
python main.py
```

## Examples

### Example 1: Simple Capture
```python
from camera_integration import initialize_camera_system, capture_image

initialize_camera_system("data/test")
success, filename = capture_image(1, "test_capture.jpg")
```

### Example 2: Capture All Cameras
```python
from camera_integration import capture_all_cameras

results = capture_all_cameras("session_1")
for camera_id, (success, result) in results.items():
    print(f"Camera {camera_id}: {'✓' if success else '✗'} {result}")
```

### Example 3: Custom Focus Setting
```python
from camera_integration import set_camera_focus, capture_image

set_camera_focus(1, 100)  # Set manual focus
capture_image(1, "focused_capture.jpg")
```

## Migration from Old System

The old camera system in `utills/camera.py` has been replaced. Key changes:

- **Old**: `from utills.camera import capture_image`
- **New**: `from camera_integration import capture_image`

- **Old**: Simple OpenCV captures
- **New**: High-resolution fswebcam captures with focus control

- **Old**: Basic file naming
- **New**: Descriptive filenames with position and timestamp information 