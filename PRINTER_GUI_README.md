# Printer GUI with Multi-Camera Preview

A comprehensive GUI that combines printer control with live multi-camera previews, featuring proper preview switching during captures just like the original camera GUI.

## Features

### 📷 Camera Preview Tab
- **Live Multi-Camera View**: All cameras visible in one window with grid layout
- **Preview Switching**: Automatically stops previews during captures and restarts them afterward
- **Focus Control**: Manual focus sliders for supported cameras
- **Individual Capture**: Capture from specific cameras
- **Batch Capture**: Capture from all cameras simultaneously
- **Real-time Status**: Live status updates for each camera

### 🖨️ Printer Control Tab
- **Printer Connection**: Connect/disconnect to printer
- **Print Job Control**: Start, stop, pause/resume print jobs
- **Progress Tracking**: Visual progress bar and status updates
- **Expandable Interface**: Ready for future printer functionality

### ⚙️ Settings Tab
- **Data Folder**: Choose where captured images are saved
- **Capture Method**: Select between fswebcam and OpenCV
- **Auto-capture**: Enable/disable automatic captures during printing

## How It Works

### Preview Management During Captures
The GUI implements the same preview switching logic as the original camera GUI:

1. **Before Capture**: Stops the preview stream for the target camera
2. **During Capture**: Performs high-resolution capture using fswebcam or OpenCV
3. **After Capture**: Restarts the preview stream automatically
4. **Status Updates**: Shows capture progress and results in real-time

### Camera Grid Layout
- **1 Camera**: Single large preview
- **2 Cameras**: Side-by-side layout
- **3+ Cameras**: 2x2 grid layout

## Installation & Setup

### Prerequisites
```bash
# Install required packages
pip install opencv-python pillow

# For Linux/Raspberry Pi
sudo apt install fswebcam v4l-utils
```

### Camera Permissions
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Set camera permissions
sudo chmod 666 /dev/video*

# Log out and back in for group changes to take effect
```

## Usage

### Starting the GUI
```bash
python test_printer_gui.py
```

### Basic Operation

1. **Camera Preview Tab**:
   - View live feeds from all connected cameras
   - Adjust focus using sliders (for supported cameras)
   - Capture individual images or all cameras at once

2. **Printer Control Tab**:
   - Connect to your printer
   - Start/stop print jobs
   - Monitor print progress

3. **Settings Tab**:
   - Set data folder for image saves
   - Choose capture method (fswebcam recommended for high quality)
   - Configure auto-capture settings

### Integration with main.py

The GUI can work alongside your existing `main.py` workflow:

```python
# In main.py, you can still use the camera integration
from camera_integration import capture_image

# The GUI will handle preview switching automatically
success, filename = capture_image(camera_id=1, method='fswebcam')
```

## Camera Configuration

The system uses the same camera configuration as `Camera/camera_manager.py`:

### Available Cameras
- **Camera 1 (video0)**: Overhead Camera
  - Capture: 8000x6000, Preview: 640x480
  - Manual focus control
  - 180° rotation

- **Camera 2 (video2)**: Side Camera
  - Capture: 1920x1080, Preview: 640x480
  - Manual focus control
  - No rotation

## File Structure

```
PrinterPython/
├── printer_gui.py              # Main GUI application
├── test_printer_gui.py         # Test script
├── camera_integration.py       # Camera integration module
├── Camera/
│   ├── camera_manager.py       # Camera management system
│   ├── gui.py                  # Original camera GUI
│   └── main_camera.py          # Camera main script
└── main.py                     # Your existing main script
```

## Extending the GUI

The GUI is designed to be easily expandable for future printer functionality:

### Adding New Printer Features
1. **New Tab**: Add tabs to the notebook in `_create_ui()`
2. **New Controls**: Add buttons, sliders, etc. to existing tabs
3. **Integration**: Connect to your existing printer control modules

### Example: Adding Temperature Control
```python
def _create_temperature_tab(self):
    """Create temperature control tab"""
    temp_frame = ttk.Frame(self.notebook)
    self.notebook.add(temp_frame, text="🌡️ Temperature")
    
    # Add temperature controls here
    ttk.Label(temp_frame, text="Nozzle Temperature").pack()
    # ... more controls
```

## Troubleshooting

### Common Issues

1. **Cameras not showing**
   - Check camera connections
   - Verify permissions: `ls -la /dev/video*`
   - Restart the application

2. **Preview not working**
   - Ensure cameras are not in use by other applications
   - Check camera permissions
   - Try restarting the camera streams

3. **Capture failures**
   - Verify fswebcam is installed: `which fswebcam`
   - Check camera focus settings
   - Ensure sufficient disk space

4. **GUI not starting**
   - Check Python dependencies: `pip list | grep -E "(opencv|pillow)"`
   - Verify tkinter is available: `python -c "import tkinter"`

### Debug Mode
Enable verbose output by setting environment variables:
```bash
export CAMERA_DEBUG=1
export GUI_DEBUG=1
python test_printer_gui.py
```

## Performance Tips

1. **Preview Resolution**: Lower preview resolution for better performance
2. **Update Rate**: Adjust update frequency in `update_loop()` if needed
3. **Memory Usage**: Close unused camera streams when not needed
4. **Disk Space**: Monitor captured image storage

## Future Enhancements

The GUI is designed for easy expansion:

- **Real-time Print Monitoring**: Live print head position tracking
- **Temperature Graphs**: Real-time temperature plotting
- **Print Job Queue**: Multiple print job management
- **Remote Control**: Web interface for remote monitoring
- **Data Logging**: Comprehensive print session logging
- **Alert System**: Notifications for print issues

## Integration Examples

### With Your Existing Code
```python
# The GUI can work alongside your existing workflow
from camera_integration import capture_image

# During printing, captures will automatically handle preview switching
def print_with_captures():
    # Your existing print logic
    for command in toolpath:
        if "CAPTURE" in command:
            # GUI will handle preview switching automatically
            success, filename = capture_image(camera_id=1)
        else:
            # Normal print command
            printer.send_gcode(command)
```

### Standalone Camera Control
```python
# Use just the camera functionality
from printer_gui import PrinterGUI
import tkinter as tk

root = tk.Tk()
app = PrinterGUI(root)
# Switch to camera tab
app.notebook.select(0)  # Camera preview tab
root.mainloop()
```

This GUI provides a solid foundation for your printer control system while maintaining the high-quality camera functionality you need! 