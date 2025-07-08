#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from datetime import datetime

from camera_integration import (
    CAMERAS,
    initialize_camera_system,
    capture_all_cameras,
    set_camera_focus,
    set_gui_instance,
    set_data_folder
)

# Global variable for print sequence control
print_sequence_started = False

class CameraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Control System")
        self.root.geometry("500x250")

        self.active_devices = []
        self.save_folder = os.getcwd()

        self._initialize_cameras()
        self._initialize_camera_integration()
        self._create_ui()

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _initialize_cameras(self):
        for camera_id, config in CAMERAS.items():
            if os.path.exists(config['node']) and os.access(config['node'], os.R_OK | os.W_OK):
                set_camera_focus(camera_id, config['focus_value'])
                self.active_devices.append(camera_id)

    def _initialize_camera_integration(self):
        initialize_camera_system(self.save_folder)
        set_gui_instance(self)

    def _create_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Camera Control System", font=('Arial', 14)).pack(pady=10)

        folder_frame = ttk.Frame(frame)
        folder_frame.pack(pady=5, fill=tk.X)

        ttk.Label(folder_frame, text="Save Folder:").pack(side=tk.LEFT)
        self.folder_var = tk.StringVar(value=self.save_folder)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=35)
        folder_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.select_save_folder).pack(side=tk.RIGHT)

        capture_btn = ttk.Button(frame, text="📷 Capture All Cameras", command=self.capture_all)
        capture_btn.pack(pady=10)

        self.status_label = ttk.Label(frame, text="Ready", foreground="green")
        self.status_label.pack(pady=5)

        ttk.Button(frame, text="🚀 Begin Print Sequence", command=self.begin_sequence).pack(pady=10)

    def select_save_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_folder)
        if folder:
            self.save_folder = folder
            self.folder_var.set(folder)
            set_data_folder(folder)

    def capture_all(self):
        self.status_label.config(text="Capturing...", foreground="orange")
        threading.Thread(target=self._do_capture_all, daemon=True).start()

    def _do_capture_all(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = capture_all_cameras(filename_prefix=f"capture_{timestamp}", method='fswebcam')
        success = all(result[0] for result in results.values())
        if success:
            self.status_label.config(text="Capture Complete", foreground="green")
        else:
            self.status_label.config(text="Capture Error", foreground="red")

    def begin_sequence(self):
        global print_sequence_started
        print_sequence_started = True
        self.status_label.config(text="Sequence Started", foreground="blue")

    def on_close(self):
        self.root.destroy()


def check_button_click():
    global print_sequence_started
    return print_sequence_started


def main():
    root = tk.Tk()
    app = CameraGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
