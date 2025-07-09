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
from g_code_comands import *
from data_collection import DataCollector
import tkinter as tk
from Camera_gui import MultiCameraApp
from configs import *
import threading

from camera_integration import (
    initialize_cameras, capture_image, capture_all_cameras,
    start_timelapse, stop_timelapse, cleanup_all,
    get_available_cameras, VIDEO_DEVICES
)
from print_utils import data_directory, save_toolpath, capture_live_print

# Global variable for print sequence control
print_sequence_started = False

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
    toolpath.extend(capture_print(camera=1, x=17.5, y=0, z=60, ))
    toolpath.extend(contracting_square_wave(start_x=40, start_y=40, height=40, width=5, iterations=5, shrink_rate=0.95, prnt=prnt))
    toolpath.extend(capture_print(camera=1, x=7.5, y=17.5, z=0, file_name="contracting_square_wave"))


    # Striaght Line Test
    toolpath.extend(straight_line(40, 90, 40, 5, 5, prnt))
    toolpath.extend(capture_print(camera=1, x=7.5, y=17.5, z=0, file_name="straight_line", time_lapse=True, time_lapse_interval=30, time_lapse_duration=1800))
    return toolpath







def main():

    # Initialize controller (localhost since running on Pi)
    klipper = KlipperController()
    klipper.connect()
    
    # Initialize loadcell
    #initialize_loadcell()
    
    # Create data folder and initialize camera system
    data_folder = data_directory()

    initialize_cameras()
    cameras = get_available_cameras()
   
    # Print available cameras and their info
    printer = MXeneProfile_pet_25G  # Example: using PET 25G profile
    capacitor_profile = stdCap  # Example: using standard capacitor
    printer.set_print_height(print_height=2.5, bed_height=2.5)

    # Enable pressure-based extrusion if needed
    # printer_profile.constPressure(target_pressure=5.0)  # Uncomment and set target pressure
    
    print(f"Printer profile: {printer}")
    print(f"Capacitor profile: {capacitor_profile}")
    print(f"Extrusion rate: {printer.extrusion}")
    print(f"Feed rate: {printer.feed_rate}")
    print(f"Print height: {printer.print_height}")
    
    data_folder = data_directory()

    toolpath = generate_toolpath(prnt=printer, cap=capacitor_profile)
    save_toolpath(toolpath, data_folder)

    #data_collector = DataCollector()
    #data_collector.record_print_data(printer, getLoad)


    print("Print sequence initiated by user!")
    
    for comand in toolpath:
        if "CAPTURE" in comand:
            try:
                capture_live_print(
                    comand=comand, 
                    klipper_ctrl=klipper, 
                    prnt=printer, 
                    file_path=data_folder)


            except Exception as e:
                print(f"✗ Error CAPTURE not taken '{comand}': {e}")
                continue
            

        #"PASUE, delay"
        elif "PASUE" in comand:

            try:
                parts = [part.strip() for part in comand.split(",")]
                delay = int(parts[1])
                klipper.wait_for_idle()
                time.sleep(delay)

            except (ValueError, IndexError) as e:
                print(f"✗ Error parsing PASUE command '{comand}': {e}")
                continue

        elif comand.strip() and not comand.strip().startswith(";"):
            klipper.send_gcode(comand)
            time.sleep(0.01)

    #data_collector.stop_record_data()
    
    # Optional: Capture final images from all cameras
    print("Capturing final images from all cameras...")
    from camera_integration import capture_all_cameras
    final_captures = capture_all_cameras(filename_prefix="final")
    
    for camera_id, (success, result) in final_captures.items():
        if success:
            print(f"✓ Final capture {camera_id}: {result}")
        else:
            print(f"✗ Final capture {camera_id} failed: {result}")
    
    print("Print sequence completed successfully!")

main()