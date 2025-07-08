#!/usr/bin/env python3
"""
Camera GUI with Timelapse Functionality
Camera preview and control system with timelapse capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
import cv2
import os
from datetime import datetime

from camera_integration import (
    CAMERAS,
    initialize_camera_system,
    capture_image,
    capture_all_cameras,
    list_cameras,
    get_camera_info,
    set_camera_focus,
    set_gui_instance
)

# Focus range constants
FOCUS_MIN, FOCUS_MAX = 0, 127

# Global variable for print sequence control
print_sequence_started = False

class CameraGUI:
    def __init__(self, root):
        self.root = root
        root.title("Camera Control with Timelapse")
        root.geometry("1400x900")
        
        # Camera system
        self.streams = {}
        self.active_devices = []
        self.focus_sliders = {}
        self.focus_values = {}
        self.video_labels = {}
        self.status_labels = {}
        self.camera_frames = {}
        
        # Timelapse state
        self.timelapse_active = False
        self.timelapse_thread = None
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
        for camera_id, config in CAMERAS.items():
            if os.path.exists(config['node']):
                if os.access(config['node'], os.R_OK | os.W_OK):
                    # Set focus for this camera
                    set_camera_focus(camera_id, config['focus_value'])
                    self.active_devices.append(camera_id)
                    # Store current focus value
                    self.focus_values[camera_id] = config['focus_value']
                    print(f"[+] Camera {camera_id} ({config['name']}) initialized")
                else:
                    print(f"[!] No permission for {config['node']}")
            else:
                print(f"[!] Camera {camera_id} ({config['node']}) not found")

    def _initialize_camera_integration(self):
        """Initialize the camera integration system"""
        try:
            # Initialize camera integration
            initialize_camera_system()
            
            # Set this GUI instance for preview management
            set_gui_instance(self)
            
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
        
        ttk.Label(title_frame, text="Camera Control with Timelapse", 
                font=('Arial', 16, 'bold')).pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Camera preview tab
        self._create_camera_tab()
        
        # Timelapse tab
        self._create_timelapse_tab()
        
        # Settings tab
        self._create_settings_tab()
        
        # Print sequence button
        self._create_print_sequence_button(main_frame)

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
        for i, camera_id in enumerate(self.active_devices):
            config = CAMERAS[camera_id]
            row = i // cols
            col = i % cols
            
            # Create camera panel
            self._create_camera_panel(parent, camera_id, config, row, col)

    def _create_camera_panel(self, parent, camera_id, config, row, col):
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
        self.video_labels[camera_id] = video_label
        
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
                command=lambda val, cid=camera_id: self._on_focus_change(cid, val)
            )
            focus_slider.set(config['focus_value'])
            focus_slider.pack(fill=tk.X, pady=2)
            
            self.focus_sliders[camera_id] = {
                'slider': focus_slider,
                'display': focus_display
            }
        else:
            ttk.Label(camera_frame, text="Focus: Auto", font=('Arial', 9, 'bold')).pack()
        
        # Individual capture button
        capture_btn = ttk.Button(
            camera_frame,
            text=f"📷 Capture {config['name']}",
            command=lambda cid=camera_id: self.capture_single(cid)
        )
        capture_btn.pack(pady=5, fill=tk.X, padx=10)
        
        # Status label
        status_label = ttk.Label(camera_frame, text="Initializing...", foreground="orange")
        status_label.pack(pady=5)
        self.status_labels[camera_id] = status_label
        
        self.camera_frames[camera_id] = camera_frame

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

    def _create_timelapse_tab(self):
        """Create the timelapse control tab"""
        timelapse_frame = ttk.Frame(self.notebook)
        self.notebook.add(timelapse_frame, text="⏱️ Timelapse Control")
        
        # Timelapse settings
        settings_frame = ttk.LabelFrame(timelapse_frame, text="Timelapse Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Camera selection
        camera_frame = ttk.Frame(settings_frame)
        camera_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(camera_frame, text="Camera:").pack(side=tk.LEFT)
        self.timelapse_camera_var = tk.StringVar(value="1")
        camera_combo = ttk.Combobox(camera_frame, textvariable=self.timelapse_camera_var, 
                                   values=[str(cid) for cid in self.active_devices], 
                                   state="readonly", width=10)
        camera_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Interval settings
        interval_frame = ttk.Frame(settings_frame)
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interval_frame, text="Interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="30")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Duration settings
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(duration_frame, text="Duration (minutes):").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="30")
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_var, width=10)
        duration_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Position settings
        pos_frame = ttk.Frame(settings_frame)
        pos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pos_frame, text="Position (X, Y, Z):").pack(side=tk.LEFT)
        self.x_pos_var = tk.StringVar(value="0")
        self.y_pos_var = tk.StringVar(value="0")
        self.z_pos_var = tk.StringVar(value="0")
        
        ttk.Entry(pos_frame, textvariable=self.x_pos_var, width=8).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Entry(pos_frame, textvariable=self.y_pos_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Entry(pos_frame, textvariable=self.z_pos_var, width=8).pack(side=tk.LEFT, padx=5)
        
        # Timelapse controls
        control_frame = ttk.LabelFrame(timelapse_frame, text="Timelapse Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start/Stop button
        self.timelapse_btn = ttk.Button(
            control_frame,
            text="▶️ Start Timelapse",
            command=self.toggle_timelapse
        )
        self.timelapse_btn.pack(pady=5)
        
        # Progress bar
        self.timelapse_progress = ttk.Progressbar(control_frame, mode='determinate')
        self.timelapse_progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Status label
        self.timelapse_status = ttk.Label(control_frame, text="Ready to start timelapse", foreground="green")
        self.timelapse_status.pack(pady=5)

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

    def _create_print_sequence_button(self, parent):
        """Create the Begin Print Sequence button"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.print_sequence_btn = ttk.Button(
            button_frame,
            text="🚀 Begin Print Sequence",
            command=self.begin_print_sequence,
            style="Accent.TButton"
        )
        self.print_sequence_btn.pack(pady=10)
        
        # Status label for print sequence
        self.print_sequence_status = ttk.Label(button_frame, text="Ready to begin print sequence", foreground="green")
        self.print_sequence_status.pack(pady=5)

    def _on_focus_change(self, camera_id, value):
        """Handle focus slider changes"""
        focus_value = int(value)
        config = CAMERAS[camera_id]
        
        # Update the display
        if camera_id in self.focus_sliders:
            self.focus_sliders[camera_id]['display'].config(text=f"Value: {focus_value}")
        
        # Update the stored value
        self.focus_values[camera_id] = focus_value
        
        # Apply focus change to camera
        def apply_focus():
            try:
                set_camera_focus(camera_id, focus_value)
                print(f"[*] Focus changed for camera {camera_id}: {focus_value}")
            except Exception as e:
                print(f"[!] Focus change failed for camera {camera_id}: {e}")
        
        # Use threading to avoid blocking the UI
        threading.Thread(target=apply_focus, daemon=True).start()

    def _start_previews(self):
        """Start preview streams for all active cameras"""
        # Note: Preview functionality simplified - using basic capture instead
        for camera_id in self.active_devices:
            self.status_labels[camera_id].config(text="Preview mode", foreground="blue")

    def capture_single(self, camera_id):
        """Capture from a single camera"""
        self.status_labels[camera_id].config(text="Capturing...", foreground="orange")
        
        # Run capture in background
        threading.Thread(target=self._do_single_capture, args=(camera_id,), daemon=True).start()

    def _do_single_capture(self, camera_id):
        """Background single capture process"""
        try:
            # Use the new camera integration system
            success, result = capture_image(camera_id=camera_id, method='fswebcam')
            
            if success:
                self.root.after(0, lambda: self.status_labels[camera_id].config(
                    text=f"✓ Saved: {result}", foreground="green"
                ))
            else:
                self.root.after(0, lambda: self.status_labels[camera_id].config(
                    text=f"✗ Failed: {result}", foreground="red"
                ))
                
        except Exception as e:
            print(f"[!] Capture error for camera {camera_id}: {e}")
            self.root.after(0, lambda: self.status_labels[camera_id].config(
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
        for camera_id in self.active_devices:
            thread = threading.Thread(target=self._do_single_capture, args=(camera_id,))
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

    def toggle_timelapse(self):
        """Toggle timelapse on/off"""
        if self.timelapse_active:
            self.stop_timelapse()
        else:
            self.start_timelapse()

    def start_timelapse(self):
        """Start timelapse capture"""
        try:
            camera_id = int(self.timelapse_camera_var.get())
            interval = int(self.interval_var.get())
            duration_minutes = int(self.duration_var.get())
            x = float(self.x_pos_var.get())
            y = float(self.y_pos_var.get())
            z = float(self.z_pos_var.get())
            
            if interval <= 0 or duration_minutes <= 0:
                messagebox.showerror("Error", "Interval and duration must be positive numbers")
                return
            
            self.timelapse_active = True
            self.timelapse_btn.config(text="⏹️ Stop Timelapse")
            self.timelapse_status.config(text="Timelapse running...", foreground="orange")
            
            # Start timelapse in background thread
            self.timelapse_thread = threading.Thread(
                target=self._run_timelapse,
                args=(camera_id, interval, duration_minutes, x, y, z),
                daemon=True
            )
            self.timelapse_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input values: {e}")

    def stop_timelapse(self):
        """Stop timelapse capture"""
        self.timelapse_active = False
        self.timelapse_btn.config(text="▶️ Start Timelapse")
        self.timelapse_status.config(text="Timelapse stopped", foreground="red")
        self.timelapse_progress.config(value=0)

    def _run_timelapse(self, camera_id, interval, duration_minutes, x, y, z):
        """Run timelapse capture in background"""
        duration_seconds = duration_minutes * 60
        total_frames = duration_seconds // interval
        captured_frames = 0
        
        start_time = time.time()
        
        while self.timelapse_active and (time.time() - start_time) < duration_seconds:
            try:
                # Capture image using the capture_live_print function logic
                timestamp = datetime.now().strftime("%H_%M_%S")
                base_filename = f"camera{camera_id}_pos_{x}_{y}_{z}_{timestamp}_timelapse"
                filename = f"{base_filename}.jpg"
                
                success, result = capture_image(camera_id=camera_id, filename=filename, method='fswebcam')
                
                if success:
                    captured_frames += 1
                    print(f"✓ Timelapse frame {captured_frames}: {result}")
                else:
                    print(f"✗ Timelapse frame failed: {result}")
                
                # Update progress
                progress = (captured_frames / total_frames) * 100
                self.root.after(0, lambda p=progress: self.timelapse_progress.config(value=p))
                
                # Sleep for interval (except for the last frame)
                if self.timelapse_active and (time.time() - start_time + interval) < duration_seconds:
                    time.sleep(interval)
                    
            except Exception as e:
                print(f"✗ Timelapse error: {e}")
                break
        
        # Update final status
        if self.timelapse_active:
            self.root.after(0, lambda: self.timelapse_status.config(
                text=f"Timelapse complete: {captured_frames} frames", foreground="green"
            ))
            self.root.after(0, lambda: self.timelapse_btn.config(text="▶️ Start Timelapse"))
            self.timelapse_active = False

    def begin_print_sequence(self):
        """Begin the print sequence - this will be called from main.py"""
        self.print_sequence_status.config(text="Print sequence initiated!", foreground="green")
        # Set global variable to signal main.py to start the print sequence
        global print_sequence_started
        print_sequence_started = True
        print("Print sequence button clicked - starting print sequence...")

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
        if self.timelapse_active:
            self.stop_timelapse()
        for stream in self.streams.values():
            stream.stop()
        time.sleep(0.1)
        self.root.destroy()

def main():
    """Main function to start the GUI"""
    root = tk.Tk()
    app = CameraGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 