#!/usr/bin/env python3
"""
Main function for automated printer movement sequence
Connects, homes, and moves through specified coordinates
"""

import sys
import time
import csv
import os
from klipper_controller import KlipperController
from utills.loadcell import getLoad, initialize_loadcell
from utills.camera import Camera
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


def main():

    # Initialize controller (localhost since running on Pi)
    print("Initializing printer controller...")
    controller = KlipperController(host="localhost", port=7125)
    
    # Initialize loadcell
    print("Initializing loadcell...")
    initialize_loadcell()
    
    # Initialize cameras
    print("Initializing cameras...")
    camera1 = Camera(camera_id=1)
    camera2 = Camera(camera_id=2)
    
    # Initialize printer and capacitor parameters
    print("Initializing printer and capacitor parameters...")
    
    # Select printer profile (choose one based on your needs)
    printer_profile = MXeneProfile_pet_25G  # Example: using PET 25G profile
    
    # Select capacitor profile (choose one based on your needs)
    capacitor_profile = stdCap  # Example: using standard capacitor
    
    # Enable pressure-based extrusion if needed
    # printer_profile.constPressure(target_pressure=5.0)  # Uncomment and set target pressure
    
    print(f"Printer profile: {printer_profile}")
    print(f"Capacitor profile: {capacitor_profile}")
    print(f"Extrusion rate: {printer_profile.extrusion}")
    print(f"Feed rate: {printer_profile.feed_rate}")
    print(f"Print height: {printer_profile.print_height}")
    



main()