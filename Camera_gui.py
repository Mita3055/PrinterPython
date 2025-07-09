#!/usr/bin/env python3
"""
Camera GUI Application
User interface for multi-camera control system
Uses camera_operations.py for all camera functionality
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
from PIL import Image, ImageTk
import cv2

# Import camera operations
from camera_integration import (
    VIDEO_DEVICES, FOCUS_MIN, FOCUS_MAX,
    check_dependencies, get_available_cameras, initialize_cameras,
    capture_image, capture_all_cameras, set_camera_focus,
    start_timelapse, stop_timelapse, is_timelapse_active,
    start_preview_stream, stop_preview_stream, get_preview_frame,
    cleanup_all
)

class MultiCameraApp:
    """Main camera GUI application"""
    
    def __init__(self, root):
        self.root = root
        root.title("Multi-Camera Still Capture System")
        root.geometry("1000x800")
        
        # Application state
        self.save_folder = os.getcwd()
        self.active_devices = []
        self.timelapse_controls = {}
        self.video_labels = {}
        self.status_labels = {}
        self.camera_frames = {}
        
        # Initialize the camera system
        self._initialize_system()
        
        # Create the user interface
        self._create_ui()
        
        # Start preview streams
        self._start_previews()
        
        # Setup event handlers
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start the GUI update loop
        self.update_loop()

    def _initialize_system(self):
        """Initialize the camera system"""
        print("Initializing camera system...")
        
        # Check dependencies first
        if not check_dependencies():
            messagebox.showerror("Dependencies Missing", 
                               "Required camera tools not found. Check console for details.")
            return
        
        # Initialize cameras
        if not initialize_cameras():
            messagebox.showwarning("No Cameras", 
                                 "No cameras could be initialized. Check connections.")
        
        # Get available cameras
        self.active_devices = get_available_cameras()
        print(f"Active devices: {self.active_devices}")

    def _create_ui(self):
        """Create the user interface"""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Multi-Camera Still Capture System", 
                font=('Arial', 16, 'bold')).pack()
        
        # Save folder selection
        self._create_folder_selection()
        
        # Camera panels
        for device_id in self.active_devices:
            config = VIDEO_DEVICES[device_id]
            self._create_camera_panel(device_id, config)
        
        # Global controls
        self._create_global_controls()

    def _create_folder_selection(self):
        """Create save folder selection UI"""
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5, fill=tk.X, padx=20)
        
        tk.Label(folder_frame, text="Save Folder:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        self.folder_label = tk.Label(folder_frame, text=self.save_folder, 
                                   bg='white', relief=tk.SUNKEN, anchor='w')
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(folder_frame, text="Browse", command=self.select_save_folder,
                 bg='lightblue').pack(side=tk.RIGHT)

    def _create_camera_panel(self, device_id: str, config: dict):
        """Create UI panel for a single camera"""
        # Main camera frame
        frame = tk.LabelFrame(self.root, text=f"{config['name']} ({config['node']})", 
                            font=('Arial', 10, 'bold'))
        frame.pack(pady=5, padx=20, fill=tk.X)
        
        # Video preview frame
        video_frame = tk.Frame(frame, bg='black', width=320, height=240)
        video_frame.pack(side=tk.LEFT, padx=10, pady=10)
        video_frame.pack_propagate(False)
        
        video_label = tk.Label(video_frame, text="Starting preview...", 
                             bg='black', fg='white')
        video_label.pack(expand=True)
        self.video_labels[device_id] = video_label
        
        # Controls frame
        controls_frame = tk.Frame(frame)
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera information
        self._create_camera_info(controls_frame, config)
        
        # Focus control
        self._create_focus_control(controls_frame, config)
        
        # Capture button
        self._create_capture_button(controls_frame, device_id, config)
        
        # Time-lapse controls
        self._create_timelapse_controls(controls_frame, device_id)
        
        # Status label
        status_label = tk.Label(controls_frame, text="Initializing...", fg="orange")
        status_label.pack(anchor='w')
        self.status_labels[device_id] = status_label
        
        # Store frame reference
        self.camera_frames[device_id] = frame

    def _create_camera_info(self, parent, config):
        """Create camera information display"""
        info_text = f"Preview: {config['preview_resolution'][0]}x{config['preview_resolution'][1]}\n"
        info_text += f"Capture: {config['capture_resolution'][0]}x{config['capture_resolution'][1]}\n"
        info_text += f"Rotation: {'180°' if config['rotate'] else 'None'}"
        
        tk.Label(parent, text=info_text, justify=tk.LEFT, 
                font=('Arial', 9)).pack(anchor='w')

    def _create_focus_control(self, parent, config):
        """Create focus control slider"""
        focus_frame = tk.Frame(parent)
        focus_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(focus_frame, text="Focus:", font=('Arial', 8)).pack(anchor='w')
        
        # Focus slider
        def on_focus_change(value):
            focus_val = int(value)
            set_camera_focus(config['node'], focus_val)
        
        focus_slider = tk.Scale(focus_frame, from_=FOCUS_MAX, to=FOCUS_MIN, 
                              orient=tk.HORIZONTAL, length=200,
                              command=on_focus_change)
        
        # Set initial focus value
        initial_focus = config['focus_value'] if config['focus_value'] is not None else FOCUS_MAX//2
        focus_slider.set(initial_focus)
        focus_slider.pack(fill=tk.X)

    def _create_capture_button(self, parent, device_id, config):
        """Create individual camera capture button"""
        capture_btn = tk.Button(
            parent,
            text=f"📷 Capture {config['name']}",
            command=lambda: self.capture_single(device_id),
            bg='blue',
            fg='white'
        )
        capture_btn.pack(pady=5, fill=tk.X)

    def _create_timelapse_controls(self, parent, device_id):
        """Create time-lapse control panel"""
        timelapse_frame = tk.LabelFrame(parent, text="Time-lapse", font=('Arial', 9, 'bold'))
        timelapse_frame.pack(pady=5, fill=tk.X)
        
        # Interval input
        interval_frame = tk.Frame(timelapse_frame)
        interval_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(interval_frame, text="Interval (seconds):", font=('Arial', 8)).pack(side=tk.LEFT)
        interval_var = tk.StringVar(value="30")
        interval_entry = tk.Entry(interval_frame, textvariable=interval_var, width=8)
        interval_entry.pack(side=tk.RIGHT)
        
        # Duration input
        duration_frame = tk.Frame(timelapse_frame)
        duration_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(duration_frame, text="Duration (seconds):", font=('Arial', 8)).pack(side=tk.LEFT)
        duration_var = tk.StringVar(value="600")
        duration_entry = tk.Entry(duration_frame, textvariable=duration_var, width=8)
        duration_entry.pack(side=tk.RIGHT)
        
        # Time-lapse button
        timelapse_btn = tk.Button(
            timelapse_frame,
            text="🎬 Start Time-lapse",
            command=lambda: self.toggle_timelapse(device_id),
            bg='purple',
            fg='white',
            font=('Arial', 8)
        )
        timelapse_btn.pack(pady=3, fill=tk.X)
        
        # Time-lapse status
        timelapse_status = tk.Label(timelapse_frame, text="Ready", fg="green", font=('Arial', 8))
        timelapse_status.pack()
        
        # Store references
        self.timelapse_controls[device_id] = {
            'interval_var': interval_var,
            'duration_var': duration_var,
            'button': timelapse_btn,
            'status': timelapse_status
        }

    def _create_global_controls(self):
        """Create global control buttons"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Capture all cameras button
        self.capture_all_btn = tk.Button(
            control_frame,
            text="📸 Capture All Cameras",
            command=self.capture_all,
            bg='green',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        self.capture_all_btn.pack(pady=5)
        
        # Global status label
        self.global_status = tk.Label(control_frame, text="Ready", fg="green")
        self.global_status.pack(pady=5)

    def _start_previews(self):
        """Start preview streams for all active cameras"""
        for device_id in self.active_devices:
            if start_preview_stream(device_id):
                self.status_labels[device_id].config(text="Preview active", fg="green")
            else:
                self.status_labels[device_id].config(text="Preview failed", fg="red")

    def select_save_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(initialdir=self.save_folder, 
                                       title="Select Save Folder")
        if folder:
            self.save_folder = folder
            self.folder_label.config(text=folder)
            print(f"[+] Save folder changed to: {folder}")

    def capture_single(self, device_id):
        """Capture from a single camera"""
        self.status_labels[device_id].config(text="Capturing...", fg="orange")
        
        # Run capture in background thread
        threading.Thread(target=self._do_single_capture, args=(device_id,), daemon=True).start()

    def _do_single_capture(self, device_id):
        """Background single capture process"""
        try:
            success, result = capture_image(device_id, self.save_folder)
            
            if self.root.winfo_exists():
                if success:
                    filename = os.path.basename(result)
                    self.root.after(0, lambda: self.status_labels[device_id].config(
                        text=f"✓ Saved: {filename}", fg="green"
                    ))
                else:
                    self.root.after(0, lambda: self.status_labels[device_id].config(
                        text=f"✗ Failed: {result}", fg="red"
                    ))
                    
        except Exception as e:
            print(f"[!] Capture error for {device_id}: {e}")
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.status_labels[device_id].config(
                    text="Capture error", fg="red"
                ))

    def capture_all(self):
        """Capture from all active cameras simultaneously"""
        self.global_status.config(text="Capturing from all cameras...", fg="orange")
        self.capture_all_btn.config(state="disabled")
        
        # Run all captures in background
        threading.Thread(target=self._do_all_captures, daemon=True).start()

    def _do_all_captures(self):
        """Background process to capture from all cameras"""
        try:
            results = capture_all_cameras(self.save_folder, "capture")
            
            # Update individual camera statuses
            for device_id, (success, result) in results.items():
                if self.root.winfo_exists():
                    if success:
                        filename = os.path.basename(result)
                        self.root.after(0, lambda did=device_id, fn=filename: 
                                      self.status_labels[did].config(text=f"✓ Saved: {fn}", fg="green"))
                    else:
                        self.root.after(0, lambda did=device_id, err=result: 
                                      self.status_labels[did].config(text=f"✗ Failed: {err}", fg="red"))
            
            # Update global status
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.global_status.config(
                    text="All captures completed", fg="green"
                ))
                self.root.after(0, lambda: self.capture_all_btn.config(state="normal"))
                
        except Exception as e:
            print(f"[!] Capture all error: {e}")
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.global_status.config(
                    text="Capture error", fg="red"
                ))
                self.root.after(0, lambda: self.capture_all_btn.config(state="normal"))

    def toggle_timelapse(self, device_id):
        """Start or stop time-lapse for a camera"""
        if is_timelapse_active(device_id):
            self.stop_timelapse_for_device(device_id)
        else:
            self.start_timelapse_for_device(device_id)

    def start_timelapse_for_device(self, device_id):
        """Start time-lapse capture for a camera"""
        controls = self.timelapse_controls[device_id]
        
        try:
            interval = float(controls['interval_var'].get())
            duration = float(controls['duration_var'].get())
            
            # Validate inputs
            if interval <= 0 or duration <= 0:
                messagebox.showerror("Error", "Interval and duration must be positive numbers")
                return
            
            if interval > duration:
                messagebox.showerror("Error", "Interval cannot be greater than duration")
                return
            
            # Start the timelapse
            if start_timelapse(device_id, interval, duration, self.save_folder):
                # Update UI
                controls['button'].config(text="⏹ Stop Time-lapse", bg='red')
                controls['status'].config(text="Starting...", fg="orange")
                
                # Start status update thread
                threading.Thread(target=self._monitor_timelapse, args=(device_id,), daemon=True).start()
                
                config = VIDEO_DEVICES[device_id]
                print(f"[+] Time-lapse started for {config['name']}: {interval}s interval, {duration}s duration")
            else:
                messagebox.showerror("Error", f"Failed to start timelapse for {device_id}")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid interval or duration values")

    def stop_timelapse_for_device(self, device_id):
        """Stop time-lapse capture for a camera"""
        if stop_timelapse(device_id):
            controls = self.timelapse_controls[device_id]
            controls['button'].config(text="🎬 Start Time-lapse", bg='purple')
            controls['status'].config(text="Stopped", fg="red")
            
            config = VIDEO_DEVICES[device_id]
            print(f"[+] Time-lapse stopped for {config['name']}")

    def _monitor_timelapse(self, device_id):
        """Monitor timelapse progress and update status"""
        while is_timelapse_active(device_id):
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.timelapse_controls[device_id]['status'].config(
                    text="Running...", fg="blue"
                ))
            time.sleep(5)  # Update every 5 seconds
        
        # Timelapse completed
        if self.root.winfo_exists():
            controls = self.timelapse_controls[device_id]
            self.root.after(0, lambda: controls['status'].config(text="Completed!", fg="green"))
            self.root.after(0, lambda: controls['button'].config(text="🎬 Start Time-lapse", bg='purple'))

    def update_loop(self):
        """Main display update loop for preview frames"""
        if not self.root.winfo_exists():
            return
        
        # Update preview displays
        for device_id in self.active_devices:
            frame = get_preview_frame(device_id)
            if frame is not None:
                try:
                    # Convert BGR to RGB and resize for display
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (320, 240))
                    
                    # Create PhotoImage and display
                    imgtk = ImageTk.PhotoImage(Image.fromarray(img))
                    label = self.video_labels[device_id]
                    label.imgtk = imgtk  # Keep a reference
                    label.configure(image=imgtk)
                    
                except Exception as e:
                    # Silently handle display errors
                    pass
        
        # Schedule next update
        self.root.after(50, self.update_loop)

    def on_close(self):
        """Clean shutdown when window is closed"""
        print("[*] Shutting down camera GUI...")
        
        # Stop all time-lapse operations
        for device_id in self.active_devices:
            if is_timelapse_active(device_id):
                stop_timelapse(device_id)
        
        # Cleanup camera system
        cleanup_all()
        
        # Small delay to ensure cleanup
        time.sleep(0.1)
        
        # Destroy the window
        self.root.destroy()

def main():
    """Main function to run the camera GUI"""
    print("=== Multi-Camera Still Capture System ===")
    
    # Print camera configuration
    for device_id, config in VIDEO_DEVICES.items():
        print(f"  {config['name']}: {config['node']}")
        print(f"    Capture: {config['capture_resolution'][0]}x{config['capture_resolution'][1]}")
        print(f"    Focus: {'Manual' if config['focus_value'] else 'Auto'}")
        print(f"    Rotation: {'180°' if config['rotate'] else 'None'}")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        return
    
    # Check camera availability
    available_cameras = get_available_cameras()
    if not available_cameras:
        print("[!] No cameras available!")
        print("Available video devices:")
        os.system("ls -la /dev/video* 2>/dev/null || echo 'No video devices found'")
        return
    
    print(f"[+] {len(available_cameras)} camera(s) ready")
    print()
    
    # Start GUI
    root = tk.Tk()
    app = MultiCameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()