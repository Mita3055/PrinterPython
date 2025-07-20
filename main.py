#!/usr/bin/env python3

from datetime import datetime
from klipper_controller import KlipperController
from g_code.g_code_comands import *
from g_code.printibility import *
from data_collection import DataCollector
from configs import *


from camera_integration import (
    initialize_cameras, 
    get_available_cameras, 
    VIDEO_DEVICES
)
from main_helper import (
    data_directory,
    save_toolpath,
    capture_live_print,
    execute_toolpath,
)


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
    
    toolpath.extend(printPrimeLine(xStart=5, yStart=10, len=10, prnt=prnt))
    toolpath.extend(printPrimeLine(xStart=10, yStart=10, len=20, prnt=prnt))
    toolpath.extend(printPrimeLine(xStart=15, yStart=10, len=40, prnt=prnt))
    toolpath.extend(moveZ(10, prnt))
    # Tool Path Generation

    # Spape Fidelity Test
    toolpath.extend(send_message("To Begin Shape Fidelity Test Hit Enter:"))
    toolpath.extend(waitForInput())
    print("Shape Fidelity Test initiated by user!")

    #toolpath.extend(lattice_3d(prnt=prnt, layer_height=0.05))

    #toolpath.extend(straight_line(prnt=prnt))


    toolpath.extend(contracting_square_wave(start_x=60, start_y=50, height=30, width=10, iterations=12, shrink_rate=0.85, prnt=prnt))
    toolpath.extend(capture_print(camera=1, x=90, y=10, z=60, file_name=f"FFT", time_lapse=False))
    
    return toolpath

def main():

    # Initialize controller (localhost since running on Pi)
    klipper = KlipperController()
    klipper.connect()

    if klipper.get_homed_axes() != ['xyz']:
        klipper.home_axes()

    klipper.get_position()



    # Initialize loadcell
    #initialize_loadcell()
    
    # Create data folder and initialize camera system
    data_folder = data_directory()

    initialize_cameras()
    cameras = get_available_cameras()
   
    # Print available cameras and their info
    printer = MXeneProfile_3pNanoParticles_22G  # Example: using PET 25G profile#
    
    printer.feed_rate = printer.feed_rate - 100
    capacitor_profile = stdCap  # Example: using standard capacitor

    printer.set_print_height(print_height=1.7, bed_height=1.7)


    # Enable pressure-based extrusion if needed
    # printer_profile.constPressure(target_pressure=5.0)  # Uncomment and set target pressure
    
    print(f"Printer profile: {printer}")
    print(f"Capacitor profile: {capacitor_profile}")
    print(f"Extrusion rate: {printer.extrusion}")
    print(f"Feed rate: {printer.feed_rate}")
    print(f"Print height: {printer.print_height}")

    print("\n \n Enter Folder Name for Print Data:")
    folder_name = input("Folder Name: ").strip()
    data_folder = data_directory(folder_name=folder_name)

    toolpath = generate_toolpath(prnt=printer, cap=capacitor_profile)
    save_toolpath(toolpath, data_folder)

    data_collector = DataCollector(data_folder)


    input("To Begin Print Sequence Hit Enter:")
    print("Print sequence initiated by user!")
    
    
    #data_collector.record_print_data(klipper, None)
    

    execute_toolpath(klipper_ctrl=klipper, printer=printer, toolpath=toolpath, data_folder=data_folder)

    #data_collector.stop_record_data()
    
    # Optional: Capture final images from all cameras

    """
    print("Capturing final images from all cameras...")
    from camera_integration import capture_all_cameras
    final_captures = capture_all_cameras(filename_prefix="final")
    
    for camera_id, (success, result) in final_captures.items():
        if success:
            print(f"✓ Final capture {camera_id}: {result}")
        else:
            print(f"✗ Final capture {camera_id} failed: {result}")
    """
    print("Print sequence completed successfully!")

main()