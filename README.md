# 3D Printer Control System

This repository contains a comprehensive 3D printer control system with pressure-based extrusion control, data collection capabilities, and automated printing workflows.

## File Structure and Purpose

### Core Control Files

#### `klipper_controller.py`
- **Purpose**: Main controller for Klipper-based 3D printers
- **Key Features**:
  - Connects to Moonraker API for printer communication
  - Provides movement control (X, Y, Z axes)
  - Supports homing operations
  - Real-time position monitoring
  - Custom G-code command execution
  - Interactive CLI interface

#### `data_collection.py`
- **Purpose**: Real-time data logging during printing operations
- **Key Features**:
  - Records position data (X, Y, Z, E) and load cell readings
  - Threaded data collection with configurable intervals
  - CSV output format for analysis
  - Automatic file creation with headers
  - Thread-safe start/stop operations

### Configuration and Utilities

#### `utills/configs.py`
- **Purpose**: Configuration classes for printer and capacitor parameters
- **Key Features**:
  - `Printer` class with extrusion, retraction, and movement parameters
  - `Capacitor` class for different capacitor designs
  - Pressure-based extrusion control settings
  - Predefined capacitor profiles (LargeCap, stdCap, electroCellCap)

#### `utills/g_code_comands.py`
- **Purpose**: G-code command generation for printer movements
- **Key Features**:
  - Movement commands with extrusion control
  - Pressure-based line segmentation
  - Retraction commands
  - Configurable feed rates and speeds

