# PrinterPython - 3D Printer Control System

A Python-based 3D printer control system with pressure feedback, camera monitoring, and automated toolpath generation.

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
