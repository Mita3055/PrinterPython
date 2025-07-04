#!/usr/bin/env python3
"""
Printer GUI with Multi-Camera Preview System
Combines printer control with live camera previews
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
import cv2
import os
from datetime import datetime

from Camera.camera_manager import (
    VIDEO_DEVICES, 
    FOCUS_MIN, 
    FOCUS_MAX,
    set_camera_focus,
    capture_still_fswebcam,
    capture_still_opencv,
    VideoStream
)

from camera_integration import (
    initialize_camera_system,
    capture_image,
    capture_all_cameras,
    list_cameras,
    get_camera_info
)

class PrinterGUI:
    def __init__(self, root):
        self.root = root
        root.title("Printer Control with Multi-Camera Preview")
        root.geometry("1400x900")
        
        # Camera system
        self.streams = {}
        self.active_devices = []
        self.focus_sliders = {}
        self.focus_values = {}
        self.video_labels = {}
        self.status_labels = {}
        self.camera_frames = {}
        
        # Printer state
        self.printer_connected = False
        self.printing_active = False
        self.data_folder = None
        
        # Initialize camera system
        self._initialize_cameras()
        
        # Initialize camera integration
        self._initialize_camera_integration()
        
        # Create UI
        self._create_ui()
        
        # Start preview streams
        self._start_previews()
        
        # Start update loop
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_loop()

    def _initialize_cameras(self):
        """Initialize camera settings and check availability"""
        for device_id, config in VIDEO_DEVICES.items():
            if os.path.exists(config['node']):
                if os.access(config['node'], os.R_OK | os.W_OK):
                    # Set focus for this camera
                    set_camera_focus(config['node'], config['focus_value'])
                    self.active_devices.append(device_id)
                    # Store current focus value
                    self.focus_values[device_id] = config['focus_value']
                    print(f"[+] {config['node']} initialized")
                else:
                    print(f"[!] No permission for {config['node']}")
            else:
                print(f"[!] Device {config['node']} not found")

    def _initialize_camera_integration(self):
        """Initialize the camera integration system"""
        try:
            # Initialize camera integration
            initialize_camera_system()
            
            # Set this GUI instance for preview management
            from camera_integration import camera_integration
            camera_integration.set_gui_instance(self)
            
            print("Camera integration initialized successfully")
        except Exception as e:
            print(f"Warning: Camera integration initialization failed: {e}")

    def _create_ui(self):
        """Create the main user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Printer Control with Multi-Camera Preview", 
                font=('Arial', 16, 'bold')).pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Camera preview tab
        self._create_camera_tab()
        
        # Printer control tab
        self._create_printer_tab()
        
        # Settings tab
        self._create_settings_tab()

    def _create_camera_tab(self):
        """Create the camera preview tab"""
        camera_frame = ttk.Frame(self.notebook)
        self.notebook.add(camera_frame, text="📷 Camera Preview")
        
        # Camera grid
        self._create_camera_grid(camera_frame)
        
        # Camera controls
        self._create_camera_controls(camera_frame)

    def _create_camera_grid(self, parent):
        """Create a grid layout for camera previews"""
        # Calculate grid layout based on number of cameras
        num_cameras = len(self.active_devices)
        
        if num_cameras == 1:
            cols = 1
        elif num_cameras == 2:
            cols = 2
        else:
            cols = 2  # 2x2 grid for 3+ cameras
        
        # Create camera preview frames
        for i, device_id in enumerate(self.active_devices):
            config = VIDEO_DEVICES[device_id]
            row = i // cols
            col = i % cols
            
            # Create camera panel
            self._create_camera_panel(parent, device_id, config, row, col)

    def _create_camera_panel(self, parent, device_id, config, row, col):
        """Create a single camera preview panel"""
        # Main frame for this camera
        camera_frame = ttk.LabelFrame(parent, text=f"{config['name']} ({config['node']})")
        camera_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Video preview frame
        video_frame = ttk.Frame(camera_frame, relief="sunken", borderwidth=2)
        video_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Video label (will be updated with actual video)
        video_label = ttk.Label(video_frame, text="Starting preview...", 
                              background="black", foreground="white")
        video_label.pack(expand=True, fill=tk.BOTH)
        self.video_labels[device_id] = video_label
        
        # Camera info
        info_text = f"Preview: {config['preview_resolution'][0]}x{config['preview_resolution'][1]}\n"
        info_text += f"Capture: {config['capture_resolution'][0]}x{config['capture_resolution'][1]}\n"
        info_text += f"Rotation: {'180°' if config['rotate'] else 'None'}"
        
        info_label = ttk.Label(camera_frame, text=info_text, font=('Arial', 9))
        info_label.pack(pady=5)
        
        # Focus controls
        if config['focus_value'] is not None:
            focus_frame = ttk.Frame(camera_frame)
            focus_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(focus_frame, text="Manual Focus:", font=('Arial', 9, 'bold')).pack(anchor='w')
            
            # Focus value display
            focus_display = ttk.Label(focus_frame, text=f"Value: {config['focus_value']}")
            focus_display.pack(anchor='w')
            
            # Focus slider
            focus_slider = ttk.Scale(
                focus_frame,
                from_=FOCUS_MIN,
                to=FOCUS_MAX,
                orient=tk.HORIZONTAL,
                command=lambda val, did=device_id: self._on_focus_change(did, val)
            )
            focus_slider.set(config['focus_value'])
            focus_slider.pack(fill=tk.X, pady=2)
            
            self.focus_sliders[device_id] = {
                'slider': focus_slider,
                'display': focus_display
            }
        else:
            ttk.Label(camera_frame, text="Focus: Auto", font=('Arial', 9, 'bold')).pack()
        
        # Individual capture button
        capture_btn = ttk.Button(
            camera_frame,
            text=f"📷 Capture {config['name']}",
            command=lambda did=device_id: self.capture_single(did)
        )
        capture_btn.pack(pady=5, fill=tk.X, padx=10)
        
        # Status label
        status_label = ttk.Label(camera_frame, text="Initializing...", foreground="orange")
        status_label.pack(pady=5)
        self.status_labels[device_id] = status_label
        
        self.camera_frames[device_id] = camera_frame

    def _create_camera_controls(self, parent):
        """Create global camera controls"""
        control_frame = ttk.LabelFrame(parent, text="Camera Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Capture all button
        self.capture_all_btn = ttk.Button(
            control_frame,
            text="📸 Capture All Cameras",
            command=self.capture_all
        )
        self.capture_all_btn.pack(pady=5)
        
        # Global status
        self.global_status = ttk.Label(control_frame, text="Ready", foreground="green")
        self.global_status.pack(pady=5)

    def _create_printer_tab(self):
        """Create the printer control tab"""
        printer_frame = ttk.Frame(self.notebook)
        self.notebook.add(printer_frame, text="🖨️ Printer Control")
        
        # Printer status
        status_frame = ttk.LabelFrame(printer_frame, text="Printer Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.printer_status_label = ttk.Label(status_frame, text="Not Connected", foreground="red")
        self.printer_status_label.pack(pady=5)
        
        # Connection controls
        conn_frame = ttk.LabelFrame(printer_frame, text="Connection")
        conn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(conn_frame, text="Connect to Printer", command=self.connect_printer).pack(pady=5)
        ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_printer).pack(pady=5)
        
        # Print controls
        print_frame = ttk.LabelFrame(printer_frame, text="Print Control")
        print_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(print_frame, text="Start Print Job", command=self.start_print).pack(pady=5)
        ttk.Button(print_frame, text="Stop Print Job", command=self.stop_print).pack(pady=5)
        ttk.Button(print_frame, text="Pause/Resume", command=self.pause_print).pack(pady=5)
        
        # Print progress
        progress_frame = ttk.LabelFrame(printer_frame, text="Print Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="No print job active")
        self.progress_label.pack(pady=5)

    def _create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Data folder settings
        folder_frame = ttk.LabelFrame(settings_frame, text="Data Folder")
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.folder_var = tk.StringVar(value="data")
        ttk.Label(folder_frame, text="Save captured images to:").pack(anchor='w', padx=10, pady=5)
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(folder_frame, text="Browse...", command=self.browse_folder).pack(pady=5)
        
        # Camera settings
        camera_settings_frame = ttk.LabelFrame(settings_frame, text="Camera Settings")
        camera_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Capture method
        ttk.Label(camera_settings_frame, text="Default capture method:").pack(anchor='w', padx=10, pady=5)
        self.capture_method_var = tk.StringVar(value="fswebcam")
        method_combo = ttk.Combobox(camera_settings_frame, textvariable=self.capture_method_var, 
                                   values=["fswebcam", "opencv"], state="readonly")
        method_combo.pack(anchor='w', padx=10, pady=5)
        
        # Auto-capture settings
        self.auto_capture_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(camera_settings_frame, text="Auto-capture during printing", 
                       variable=self.auto_capture_var).pack(anchor='w', padx=10, pady=5)

    def _on_focus_change(self, device_id, value):
        """Handle focus slider changes"""
        focus_value = int(value)
        config = VIDEO_DEVICES[device_id]
        
        # Update the display
        if device_id in self.focus_sliders:
            self.focus_sliders[device_id]['display'].config(text=f"Value: {focus_value}")
        
        # Update the stored value
        self.focus_values[device_id] = focus_value
        
        # Apply focus change to camera
        def apply_focus():
            try:
                set_camera_focus(config['node'], focus_value)
                print(f"[*] Focus changed for {config['name']}: {focus_value}")
            except Exception as e:
                print(f"[!] Focus change failed for {config['name']}: {e}")
        
        # Use threading to avoid blocking the UI
        threading.Thread(target=apply_focus, daemon=True).start()

    def _start_previews(self):
        """Start preview streams for all active cameras"""
        for device_id in self.active_devices:
            config = VIDEO_DEVICES[device_id]
            stream = VideoStream(config)
            if stream.start():
                self.streams[device_id] = stream
                self.status_labels[device_id].config(text="Preview active", foreground="green")
            else:
                self.status_labels[device_id].config(text="Preview failed", foreground="red")

    def capture_single(self, device_id):
        """Capture from a single camera"""
        config = VIDEO_DEVICES[device_id]
        self.status_labels[device_id].config(text="Capturing...", foreground="orange")
        
        # Run capture in background
        threading.Thread(target=self._do_single_capture, args=(device_id,), daemon=True).start()

    def _do_single_capture(self, device_id):
        """Background single capture process"""
        config = VIDEO_DEVICES[device_id]
        
        try:
            # Try fswebcam first, fallback to OpenCV
            success, message = capture_still_fswebcam(config, self)
            
            if not success:
                print(f"[*] fswebcam failed for {device_id}, trying OpenCV...")
                success, message = capture_still_opencv(config, self)
            
            if success:
                self.root.after(0, lambda: self.status_labels[device_id].config(
                    text=f"✓ Saved: {message}", foreground="green"
                ))
            else:
                self.root.after(0, lambda: self.status_labels[device_id].config(
                    text=f"✗ Failed: {message}", foreground="red"
                ))
                
        except Exception as e:
            print(f"[!] Capture error for {device_id}: {e}")
            self.root.after(0, lambda: self.status_labels[device_id].config(
                text="Capture error", foreground="red"
            ))

    def capture_all(self):
        """Capture from all active cameras simultaneously"""
        self.global_status.config(text="Capturing from all cameras...", foreground="orange")
        self.capture_all_btn.config(state="disabled")
        
        # Run all captures in background
        threading.Thread(target=self._do_all_captures, daemon=True).start()

    def _do_all_captures(self):
        """Background process to capture from all cameras"""
        capture_threads = []
        
        # Start all captures
        for device_id in self.active_devices:
            thread = threading.Thread(target=self._do_single_capture, args=(device_id,))
            thread.start()
            capture_threads.append(thread)
        
        # Wait for all to complete
        for thread in capture_threads:
            thread.join()
        
        # Update UI
        self.root.after(0, lambda: self.global_status.config(
            text="All captures completed", foreground="green"
        ))
        self.root.after(0, lambda: self.capture_all_btn.config(state="normal"))

    def connect_printer(self):
        """Connect to the printer"""
        # TODO: Implement printer connection
        self.printer_connected = True
        self.printer_status_label.config(text="Connected", foreground="green")
        messagebox.showinfo("Printer", "Printer connected successfully!")

    def disconnect_printer(self):
        """Disconnect from the printer"""
        # TODO: Implement printer disconnection
        self.printer_connected = False
        self.printer_status_label.config(text="Not Connected", foreground="red")
        messagebox.showinfo("Printer", "Printer disconnected")

    def start_print(self):
        """Start a print job"""
        if not self.printer_connected:
            messagebox.showerror("Error", "Please connect to printer first")
            return
        
        # TODO: Implement print job start
        self.printing_active = True
        messagebox.showinfo("Print", "Print job started")

    def stop_print(self):
        """Stop the current print job"""
        # TODO: Implement print job stop
        self.printing_active = False
        messagebox.showinfo("Print", "Print job stopped")

    def pause_print(self):
        """Pause/resume the current print job"""
        # TODO: Implement print pause/resume
        messagebox.showinfo("Print", "Print job paused/resumed")

    def browse_folder(self):
        """Browse for data folder"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Select Data Folder")
        if folder:
            self.folder_var.set(folder)

    def update_loop(self):
        """Main display update loop"""
        for device_id, stream in self.streams.items():
            if stream.frame is not None:
                try:
                    # Convert BGR to RGB and resize for display
                    img = cv2.cvtColor(stream.frame, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (320, 240))
                    
                    # Create PhotoImage and display
                    imgtk = ImageTk.PhotoImage(Image.fromarray(img))
                    label = self.video_labels[device_id]
                    label.imgtk = imgtk  # Keep a reference
                    label.configure(image=imgtk)
                    
                except Exception as e:
                    print(f"[!] Display update error for {device_id}: {e}")
        
        # Schedule next update
        self.root.after(50, self.update_loop)

    def on_close(self):
        """Clean shutdown"""
        print("[*] Shutting down...")
        for stream in self.streams.values():
            stream.stop()
        time.sleep(0.1)
        self.root.destroy()

def main():
    """Main function to start the GUI"""
    root = tk.Tk()
    app = PrinterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 