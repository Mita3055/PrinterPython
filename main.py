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
from loadcell import getLoad


"""
Steps:

1. Initialize the printer controller
2. Initialize the ballance
3. Initialize the cameras
3. Reset Nozzle Offset Variable
4. Load the ToolPath For the Printer
5. Home the printer
6. Begin Recording Data
8. * Printer Operations *


"""
"""
- In toolpath save tooplath as a txt file
- Add Camera Move Idicators Example: ;CAPTURE: camera_id

"""



def main():

    # Initialize controller (localhost since running on Pi)
    print("Initializing printer controller...")
    controller = KlipperController(host="localhost", port=7125)
    
    
    # Show initial position
    print("\nInitial position:")
    controller.print_position()
    
    # Step 2: Home the printer
    print("\n2. Homing printer...")
    controller.home_axes("XYZ")
    controller.print_position()
    
    # Step 3: Move to X=30 Y=30
    print("✓ Reached X=30 Y=30")
    controller.print_position()
    
    # Small pause between moves
    time.sleep(1)
    
    # Step 4: Move to X=60 Y=30
    print("\n4. Moving to X=60 Y=30...")
    controller.move_to(x=60, y=30, feedrate=3000)
    controller.print_position()

    # Loadcell example usage
    weight = getLoad()
    print(f"Loadcell reading: {weight:.3f} kg")

def record_print_data(x, y, z, e, loadcell_reading, start_time, filename="print_data.csv"):
    """
    Records the XYZE positions, loadcell reading, and elapsed time into a CSV file.
    t=0 is the moment this function is first called (start_time).
    """
    file_exists = os.path.isfile(filename)
    t = time.time() - start_time

    with open(filename, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['time_s', 'X', 'Y', 'Z', 'E', 'loadcell_kg'])
        writer.writerow([f"{t:.3f}", x, y, z, e, f"{loadcell_reading:.5f}"])


main()