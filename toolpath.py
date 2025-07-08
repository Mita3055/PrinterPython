from configs import *
from g_code_comands import *


def generate_toolpath(prnt, cap):
    """
    Generate a toolpath list of G-code commands and custom commands for the print sequence.
    Arguments:
        prnt: Printer profile object (from configs)
        cap: Capacitor profile object (from configs)
    Returns:
        toolpath: list of commands (strings)
    """
    toolpath = []

    # Example: Home axes
    toolpath.append("G28 ; Home all axes")

    # Example: Move to start position
    toolpath.append(f"G1 Z{prnt.bed_height:.2f} F{prnt.movement_speed}")

    # Example: Custom print moves (replace with actual toolpath logic)
    # This is a placeholder. In practice, you would generate lines/arcs/paths here.
    for i in range(5):
        x = 10 + i * 5
        y = 10
        z = prnt.print_height
        toolpath.append(f"G1 X{x:.2f} Y{y:.2f} Z{z:.2f} F{prnt.feed_rate}")

        # Example: Insert a CAPTURE command at each step
        # Format: "CAPTURE, camera, x, y, z, img_name, time_lapse, [interval], [duration]"
        img_name = f"step_{i}"
        toolpath.append(f"CAPTURE,1,{x},{y},{z},{img_name},False")

    # Example: End print
    toolpath.append("G1 Z10 F3000 ; Move Z up")
    toolpath.append("M104 S0 ; Turn off extruder")
    toolpath.append("M140 S0 ; Turn off bed")
    toolpath.append("M84 ; Disable motors")

    return toolpath

def save_toolpath(toolpath, folder, filename="toolpath.txt"):
    """
    Save the toolpath list to a file in the specified folder.
    Arguments:
        toolpath: list of command strings
        folder: directory to save the file
        filename: name of the file (default: toolpath.txt)
    """
    import os
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w") as f:
        for cmd in toolpath:
            f.write(cmd + "\n")
    print(f"Toolpath saved to {filepath}")



