#!/usr/bin/env python3
"""
Main function for automated printer movement sequence
Connects, homes, and moves through specified coordinates
"""

import sys
import time
import csv
import os
from datetime import datetime
from klipper_controller import KlipperController
from utills.loadcell import getLoad, initialize_loadcell
from utills.camera import initialize_cameras, start_recording, capture_image, set_camera_focus, open_preview, close_preview, release_cameras, camera_system
from utills.g_code_comands import *
from data_collection import DataCollector
from configs import *


"""
Steps:

1. Initialize the printer controller
2. Initialize the ballance and loadcell
3. Initialize the cameras
3. Reset Nozzle Offset Variable
4. Load the ToolPath For the Printer
5. Home the printer
6. Begin Recording Data
8. * Printer Operations *


"""

"""
data:

- create folder for each print with timestamp as name
- save toolpath to folder
-save data to folder
-save camera images to folder

"""

"""
- In toolpath save tooplath as a txt file
- Break down linear print commands into 1mm steps
- Add Camera Move Idicators Example: ;CAPTURE: camera_id, X, Y, Z


- for pressure passed extrussion 
    - if printing measure the pressure based on the loadcell reading
    - feed to the pressure controller
    - Given current extrussion seed and pressure passed through, determin new extrussion seed
    - given extrussion speed determin E value and apend it to the current g code command
    -  send the g code command to the printer


"""


def generate_toolpath(prnt, cap):
    toolpath = []

    toolpath.extend(home())
    toolpath.extend(printPrimeLine(xStart=5, yStart=10, len=10, prnt=prnt))
    toolpath.extend(printPrimeLine(xStart=10, yStart=10, len=10, prnt=prnt))
    toolpath.extend(printPrimeLine(xStart=15, yStart=10, len=10, prnt=prnt))
    # Tool Path Generation
    toolpath = []

    # Spape Fidelity Test
    toolpath.extend(lattice(start_x=10, start_y=40, rows=5, cols=5, spacing=3, prnt=prnt))
    toolpath.extend(capture_print(camera=1, x=17.5, y=0, z=60, prnt=prnt))
    toolpath.extend(contracting_square_wave(start_x=40, start_y=40, height=40, width=5, iterations=5, shrink_rate=0.95, prnt=prnt))
    #toolpath.extend(capture_print(camera=1, x=7.5, y=17.5, z=0, prnt=prnt))


    # Striaght Line Test
    toolpath.extend(straight_line(40, 90, 40, 5, 5, prnt))
    #toolpath.extend(capture_print(camera=1, x=7.5, y=17.5, z=0, prnt=prnt))
    return toolpath

def data_directory():
    """
    Create a timestamped directory within the data folder.
    Returns the folder name in format MonthMM_DD_HH_MM_SS
    """
    
    
    # Create data folder if it doesn't exist
    data_folder = "data"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # Generate timestamp in the required format
    timestamp = datetime.now().strftime("%m_%d_%H_%M_%S")
    
    # Create the full path for the new directory
    new_dir_path = os.path.join(data_folder, timestamp)
    
    # Create the directory
    os.makedirs(new_dir_path, exist_ok=True)
    
    print(f"Created timestamped directory: {new_dir_path}")
    return timestamp

def save_toolpath(toolpath, data_folder):
        """
        Save the toolpath as a G-code file
        """
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%m_%d_%H_%M_%S")
        filename = f"toolpath_{timestamp}.gcode"
        filepath = os.path.join(data_folder, filename)
        
        try:
            with open(filepath, 'w') as f:
                # Write G-code header
                f.write("; Toolpath generated by MXene printer\n")
                f.write(f"; Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("; Format: G1 X<x> Y<y> Z<z> E<extrusion>\n\n")
                
                # Write each toolpath point as G-code
                for i, point in enumerate(toolpath):
                    x, y, z, e = point
                    f.write(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} E{e:.3f}\n")
                
                f.write("\n; End of toolpath\n")
            
            print(f"✓ Toolpath saved as G-code: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"✗ Error saving toolpath: {e}")
            return None


def main():

    # Initialize controller (localhost since running on Pi)
    print("Initializing printer controller...")
    printer = KlipperController(host="localhost", port=7125)
    
    # Initialize loadcell
    print("Initializing loadcell...")
    initialize_loadcell()
    
    # Initialize cameras with specific configurations
    print("Initializing cameras...")
    from utills.camera import initialize_cameras, start_recording, capture_image, set_camera_focus, open_preview, close_preview, release_cameras, camera_system
    
    data_folder = data_directory()
    
    # Open camera preview
    
    # Initialize printer and capacitor parameters
    print("Initializing printer and capacitor parameters...")
    
    # Select printer profile (choose one based on your needs)
    printer_profile = MXeneProfile_pet_25G  # Example: using PET 25G profile
    capacitor_profile = stdCap  # Example: using standard capacitor
    
    # Enable pressure-based extrusion if needed
    # printer_profile.constPressure(target_pressure=5.0)  # Uncomment and set target pressure
    
    print(f"Printer profile: {printer_profile}")
    print(f"Capacitor profile: {capacitor_profile}")
    print(f"Extrusion rate: {printer_profile.extrusion}")
    print(f"Feed rate: {printer_profile.feed_rate}")
    print(f"Print height: {printer_profile.print_height}")
    
    data_folder = data_directory()

    toolpath = generate_toolpath(prnt=printer_profile, cap=capacitor_profile)
    save_toolpath(toolpath, data_folder)

    data_collector = DataCollector()
    data_collector.record_print_data(printer, getLoad)

    for comand in toolpath:
        if "CAPTURE" in comand:
            camera = comand.split(",")[1]
            x = comand.split(",")[2]
            y = comand.split(",")[3]
            z = comand.split(",")[4]

            print(f"Capturing image from camera {camera} at {x}, {y}, {z}")
            printer.send_gcode(absolute()[0])
            printer.send_gcode(movePrintHead(x, y, z, printer_profile)[0])
            
            capture_image(int(camera), os.path.join(data_folder, f"camera{camera}_{datetime.now().strftime('%H_%M_%S')}.png"))
            time.sleep(1)

        else:
            printer.send_gcode(comand)

    data_collector.stop_record_data()
    
main()