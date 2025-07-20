#!/usr/bin/env python3
import subprocess
import tkinter as tk
from tkinter import ttk

# Camera node
DEVICE_NODE = '/dev/video0'

# Function to set camera control
def set_control(control, value):
    subprocess.run(["v4l2-ctl", "-d", DEVICE_NODE, f"--set-ctrl={control}={value}"])

# Create GUI
root = tk.Tk()
root.title("Camera Control Panel")

controls = [
    ("Brightness", "brightness", 0, 64, 32),
    ("Contrast", "contrast", 0, 64, 34),
    ("Saturation", "saturation", 0, 64, 32),
    ("Hue", "hue", 0, 64, 32),
    ("Gamma", "gamma", 0, 64, 32),
    ("Sharpness", "sharpness", 0, 64, 32),
    ("Zoom", "zoom_absolute", 0, 16384, 0),
    ("Focus (Manual)", "focus_absolute", 0, 127, 120),
    ("Exposure Time", "exposure_time_absolute", 10, 1250, 330),
    ("White Balance Temp", "white_balance_temperature", 2700, 10000, 6500),
]

bool_controls = [
    ("Auto White Balance", "white_balance_automatic", 1),
    ("Auto Focus", "focus_automatic_continuous", 0),
]

menu_controls = [
    ("Power Line Frequency", "power_line_frequency", {0: "Disabled", 1: "50 Hz", 2: "60 Hz"}, 0),
    ("Auto Exposure Mode", "auto_exposure", {1: "Manual Mode", 3: "Aperture Priority"}, 3),
]

# Slider Controls
for label, control, min_val, max_val, default in controls:
    frame = tk.Frame(root)
    frame.pack(fill="x", padx=10, pady=5)

    tk.Label(frame, text=label, width=20).pack(side="left")
    slider = tk.Scale(frame, from_=min_val, to=max_val, orient="horizontal", length=300,
                      command=lambda val, c=control: set_control(c, val))
    slider.set(default)
    slider.pack(side="right")

# Boolean Controls
for label, control, default in bool_controls:
    frame = tk.Frame(root)
    frame.pack(fill="x", padx=10, pady=5)

    var = tk.IntVar(value=default)
    chk = tk.Checkbutton(frame, text=label, variable=var,
                         command=lambda c=control, v=var: set_control(c, v.get()))
    chk.pack(anchor="w")

# Menu Controls
for label, control, options, default in menu_controls:
    frame = tk.Frame(root)
    frame.pack(fill="x", padx=10, pady=5)

    tk.Label(frame, text=label, width=20).pack(side="left")
    combo = ttk.Combobox(frame, values=list(options.values()), state="readonly")
    combo.current(list(options.keys()).index(default))
    combo.pack(side="right")

    def menu_callback(event, c=control, o=options):
        selection = combo.get()
        value = [k for k, v in o.items() if v == selection][0]
        set_control(c, value)

    combo.bind("<<ComboboxSelected>>", menu_callback)

root.mainloop()
