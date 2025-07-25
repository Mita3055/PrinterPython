# PrinterPython - DIW 3D Printer Control System

A Python-based 3D printer control system with pressure feedback, camera monitoring, and automated toolpath generation.

## Quick Setup for Raspberry Pi

### Switch to Raspberry Pi Branch and Sync with Main

Copy and paste these commands to switch to the Raspberry Pi branch and make it identical to main:

```bash
# Switch to Raspberry Pi branch
git checkout Raspberri-Pi

# Fetch latest changes from remote
git fetch origin

# Reset Raspberry Pi branch to match main branch exactly
git reset --hard origin/main

# Push the updated Raspberry Pi branch to remote
git push origin Raspberri-Pi --force
```

##  Overview

PrinterPython is a comprehensive control system designed for advanced 3D printing applications, particularly focused on materials research and precision printing. It provides real-time pressure feedback, multi-camera monitoring, automated data collection, and sophisticated toolpath generation capabilities.

##  File Structure

```
PrinterPython/
├── main.py                     # Main entry point
├── configs.py                  # Printer and capacitor profiles
├── data_collection.py          # Real-time data logging
├── main_helper.py              # Helper functions for execution
├── printer_cli.py              # Command-line interface
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── hardware/                   # Hardware interfaces
│   ├── klipper_controller.py   # Klipper/Moonraker communication
│   ├── camera_integration.py   # Multi-camera system
│   ├── mettler_scale.py        # Scale integration
│   └── ...
│
├── g_code/                     # G-code generation
│   ├── __init__.py
│   ├── comands.py              # Basic G-code commands
│   ├── patterns.py             # Print patterns (lattices, capacitors)
│   └── printibility.py        # Printability tests
│
├── tools/                      # GUI and utilities
│   ├── camera_gui.py           # Main camera GUI
│   ├── g_code_generator.py     # G-code generation GUI
│   └── Camera_ctlr.py          # Camera control panel
│
├── utills/                     # Utility modules
│   ├── camera.py               # Camera utilities
│   ├── loadcell.py             # Load cell calibration
│   └── pressure_controller.py  # Pressure feedback control
│
├── docs/                       # Documentation
│   ├── cam1.txt                # Camera specifications
│   ├── output.txt              # Example output logs
│   └── output2.txt
│
└── data/                       # Generated during runs
    └── [timestamped folders]   # Print data, images, toolpaths
```

##  Quick Start

### Prerequisites

1. **Hardware Requirements:**
   - Raspberry Pi (tested on Pi 4)
   - Klipper-based 3D printer with Moonraker
   - USB cameras (up to 3 supported)
   - Optional: Load cell for pressure feedback
   - Optional: Mettler Toledo scale

2. **Software Requirements:**
   - Python 3.7+
   - Klipper firmware running on printer
   - Moonraker API server (default port 7125)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PrinterPython
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies (Raspberry Pi):**
   ```bash
   sudo apt update
   sudo apt install fswebcam v4l-utils
   ```

4. **Configure cameras (if using):**
   ```bash
   # List available video devices
   ls /dev/video*
   
   # Test camera
   fswebcam -d /dev/video0 test.jpg
   ```

### Basic Usage

1. **Run the main system:**
   ```bash
   python main.py
   ```

2. **Use the command-line interface:**
   ```bash
   python printer_cli.py
   ```

3. **Launch the GUI (if available):**
   ```bash
   python tools/printer_gui.py
   ```

##  Configuration

### Printer Profiles

Edit `configs.py` to configure printer settings:

```python
# Example printer profile
MXeneProfile_25G = Printer(
    extrusion=0.015,
    retraction=0.04,
    feed_rate=1650,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
)
```

**Available Profiles:**
- `pvaPrintProfile` - PVA material settings
- `MXeneProfile_*` - Various MXene ink configurations
- `MXeneProfile_pet_25G/30G` - PET substrate settings
- `MXeneProfile_*pNanoParticles_*` - Nanoparticle-enhanced inks

### Capacitor Profiles

Configure capacitor printing patterns:

```python
# Example capacitor profile
stdCap = Capacitor(
    stem_len=10,
    arm_len=10,
    arm_count=4,
    gap=3,
    arm_gap=4,
    contact_patch_width=3
)
```

### Camera Configuration

Configure cameras in `configs.py`:

```python
VIDEO_DEVICES = {
    'video0': {
        'node': '/dev/video0',
        'capture_resolution': (8000, 6000),
        'preview_resolution': (640, 480),
        'focus_value': 120,
        'rotate': True,
        'name': 'Camera_0'
    }
}
```

##  Usage Instructions

### Main System (`main.py`)

The main system provides a complete printing workflow:

1. **Initialize hardware** (printer, cameras, sensors)
2. **Select printer and capacitor profiles**
3. **Generate toolpath** using built-in patterns
4. **Execute print sequence** with real-time monitoring
5. **Collect data** and capture images automatically

```bash
python main.py
```

**Interactive prompts:**
- Enter folder name for print data
- Confirm print sequence initiation
- Monitor progress via console output

### Command-Line Interface (`printer_cli.py`)

Comprehensive CLI for selecting profiles and executing routines:

```bash
python printer_cli.py
```

**Features:**
- Profile selection (printer + capacitor)
- Routine selection (lattice, square wave, capacitor printing, etc.)
- Parameter configuration
- Automated execution with data collection

### GUI Tools

1. **Main Printer GUI:**
   ```bash
   python tools/printer_gui.py
   ```

2. **G-Code Generator:**
   ```bash
   python tools/g_code_generator.py
   ```

3. **Camera Control Panel:**
   ```bash
   python tools/Camera_ctlr.py
   ```

## Print Patterns and Functions

### Available Patterns

1. **Basic Patterns:**
   - `lattice()` - Grid/lattice structures
   - `square_wave()` - Square wave patterns
   - `contracting_square_wave()` - Tapered square waves
   - `straight_line()` - Line tests for calibration

2. **Capacitor Patterns:**
   - `printCap()` - Basic capacitor structure
   - `printCap_contact_patch()` - Capacitor with contact patches
   - `singleLineCap_left/right()` - Single-sided capacitors

3. **Advanced Patterns:**
   - `lattice_3d()` - Multi-layer lattice structures
   - `layered_FFT()` - Frequency-domain test patterns

### Custom Toolpath Generation

```python
# Example toolpath generation
def generate_custom_toolpath(printer, capacitor):
    toolpath = []
    
    # Add start sequence
    toolpath.extend(absolute())
    toolpath.extend(home())
    
    # Add patterns
    toolpath.extend(lattice(start_x=60, start_y=50, rows=5, cols=5, spacing=3, prnt=printer))
    toolpath.extend(capture_print(camera=1, x=90, y=10, z=60, file_name="lattice_test"))
    
    # Add end sequence
    toolpath.extend(moveZ(10, printer))
    
    return toolpath
```

##  Camera System

### Multi-Camera Support

- **Camera 1**: High-resolution image capture with focus control
- **Camera 2**: Continuous video recording (side view)
- **Camera 3**: Continuous video recording (alternative angle)

### Camera Functions

```python
# Initialize cameras
initialize_cameras()

# Capture image
capture_image(device_id='video0', save_path='./images', filename='test.jpg')

# Start timelapse
start_timelapse(device_id='video0', interval_seconds=30, duration_seconds=1800, save_path='./timelapse')
```

### Image Capture During Printing

Images are automatically captured at specified coordinates:

```python
# In toolpath
toolpath.extend(capture_print(camera=1, x=90, y=10, z=60, file_name="progress_01"))
```

##  Data Collection

### Automatic Data Logging

The system automatically logs:
- Printer position (X, Y, Z, E) in real-time
- Load cell readings (if connected)
- Timestamps for all events
- Camera capture events

### Data Structure

```
data/
└── [experiment_name]_MM_DD_HH_MM_SS/
    ├── print_data.csv          # Real-time printer data
    ├── toolpath_MM_DD_HH_MM_SS.gcode  # Generated G-code
    ├── Camera_0_timestamp.jpg  # Captured images
    ├── Camera_2_timestamp.jpg
    └── timelapse_*/            # Timelapse sequences
```

##  Advanced Features

### Pressure-Based Extrusion Control

Enable pressure feedback for consistent extrusion:

```python
# Enable pressure control
printer.constPressure(target_pressure=5.0)  # 5 Newtons target

# The system will automatically adjust extrusion rates based on load cell feedback
```

### Custom Commands in Toolpaths

Special commands for advanced control:

```python
# Pause for specified seconds
toolpath.extend(pause(delay=30))

# Wait for user input
toolpath.extend(waitForInput())

# Send message to console
toolpath.extend(send_message("Change material now"))

# Capture with timelapse
toolpath.extend(capture_print(camera=1, x=0, y=0, z=60, time_lapse=True, 
                             time_lapse_interval=30, time_lapse_duration=1800))
```

##  Hardware Setup

### Klipper Configuration

Ensure your `printer.cfg` includes:

```ini
[virtual_sdcard]
path: ~/gcode_files

[display_status]

[pause_resume]

[gcode_macro PAUSE]
# ... pause macro

[gcode_macro RESUME]
# ... resume macro
```

### Load Cell Setup (Optional)

1. Connect HX711 load cell amplifier to GPIO pins
2. Update pin assignments in `utills/loadcell.py`
3. Run calibration:
   ```bash
   python utills/loadcell.py --calibrate
   ```

### Camera Setup

1. Connect USB cameras to Raspberry Pi
2. Verify device nodes: `ls /dev/video*`
3. Update camera configurations in `configs.py`
4. Test cameras: `python -c "from hardware.camera_integration import *; initialize_cameras()"`

##  Troubleshooting

### Common Issues

1. **Printer Connection Failed:**
   ```bash
   # Check Moonraker status
   sudo systemctl status moonraker
   
   # Check if port 7125 is open
   ss -tulpn | grep :7125
   ```

2. **Camera Not Found:**
   ```bash
   # List video devices
   v4l2-ctl --list-devices
   
   # Test camera
   fswebcam -d /dev/video0 --list-controls
   ```

3. **Import Errors:**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   
   # Check Python path
   python -c "import sys; print('\n'.join(sys.path))"
   ```

### Debug Mode

Enable debug output by modifying the camera integration:

```python
# In hardware/camera_integration.py
initialize_cameras(debug=True)
```

