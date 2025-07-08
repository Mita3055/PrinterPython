# PrinterPython - 3D Printer Control System

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

### Alternative: Create Fresh Raspberry Pi Branch

If you want to create a new Raspberry Pi branch from main:

```bash
# Switch to main branch
git checkout main

# Create and switch to new Raspberry Pi branch
git checkout -b Raspberri-Pi

# Push the new branch to remote
git push origin Raspberri-Pi
```

## Core Modules

### Main Control (`main.py`)
- **KlipperController**: 3D printer communication and control
- **DataCollector**: Real-time data logging and analysis
- **Camera System**: Multi-camera monitoring and recording
- **Pressure Controller**: Real-time extrusion rate adjustment
- **Toolpath Generator**: Automated G-code generation

### Key Functions

#### Printer Control
- `generate_toolpath()`: Creates G-code toolpath with patterns
- `save_toolpath()`: Saves toolpath to timestamped directory
- `data_directory()`: Creates organized data folders

#### Camera System (`utills/camera.py`)
- `initialize_cameras()`: Setup cameras 1, 2, 3
- `start_recording()`: Continuous video recording (cameras 2&3)
- `capture_image()`: Single image capture (camera 1)
- `set_camera_focus()`: Adjust camera focus
- `open_preview()` / `close_preview()`: Live camera preview

#### Pressure Control (`pressure_controller.py`)
- `pressure_passed_extrusion()`: Real-time extrusion rate adjustment
- `PressureController`: PD controller for pressure feedback

#### G-Code Commands (`utills/g_code_comands.py`)
- `printX()`, `printY()`: Extrusion movements
- `movePrintHead()`: Position control
- `lattice()`, `square_wave()`: Pattern generation
- `capture_print()`: Camera trigger commands

#### Data Collection (`data_collection.py`)
- `DataCollector`: Real-time loadcell and sensor data logging

#### Hardware Interfaces
- `klipper_controller.py`: Klipper firmware communication
- `utills/loadcell.py`: Load cell pressure measurement
- `mettler_scale.py`: Scale integration

## Configuration (`configs.py`)
- Printer profiles (extrusion rates, speeds, heights)
- Capacitor patterns and dimensions
- Material-specific settings

## Usage
```bash
python main.py
```

## Features
- Multi-camera monitoring and recording
- Real-time pressure-based extrusion control
- Automated toolpath generation
- Comprehensive data logging
- Pattern printing (lattices, waves, capacitors)
- Focus-adjustable image capture
