import cv2
import numpy as np
import os
import threading
import time
from datetime import datetime

# Camera system for Raspberry Pi
# Camera 1: Image capture with focus control
# Camera 2 & 3: Continuous video recording
# Preview functionality for all cameras

class CameraSystem:
    def __init__(self):
        self.cameras = {}
        self.recording_threads = {}
        self.preview_active = False
        self.preview_thread = None
        
    def initialize_camera(self, camera_id, resolution=(1920, 1080)):
        """Initialize a camera with specified resolution"""
        try:
            cap = cv2.VideoCapture(camera_id)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            
            if not cap.isOpened():
                print(f"Failed to open camera {camera_id}")
                return False
                
            self.cameras[camera_id] = cap
            print(f"Camera {camera_id} initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing camera {camera_id}: {e}")
            return False
    
    def set_focus(self, camera_id, focus_value):
        """Set focus for camera (works best with camera 1)"""
        if camera_id in self.cameras:
            self.cameras[camera_id].set(cv2.CAP_PROP_FOCUS, focus_value)
            print(f"Camera {camera_id} focus set to {focus_value}")
    
    def capture_image(self, camera_id, filename, focus_value=None):
        """Capture a single image from specified camera"""
        if camera_id not in self.cameras:
            print(f"Camera {camera_id} not initialized")
            return False
            
        try:
            if focus_value is not None:
                self.set_focus(camera_id, focus_value)
                
            ret, frame = self.cameras[camera_id].read()
            if ret:
                cv2.imwrite(filename, frame)
                print(f"Image captured: {filename}")
                return True
            else:
                print(f"Failed to capture image from camera {camera_id}")
                return False
                
        except Exception as e:
            print(f"Error capturing image: {e}")
            return False
    
    def start_recording(self, camera_id, output_folder, filename_prefix="video"):
        """Start continuous video recording for cameras 2 & 3"""
        if camera_id not in self.cameras:
            print(f"Camera {camera_id} not initialized")
            return False
            
        if camera_id in self.recording_threads and self.recording_threads[camera_id].is_alive():
            print(f"Camera {camera_id} is already recording")
            return False
            
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Start recording thread
        thread = threading.Thread(target=self._record_video, 
                                args=(camera_id, output_folder, filename_prefix))
        thread.daemon = True
        thread.start()
        self.recording_threads[camera_id] = thread
        
        print(f"Started recording camera {camera_id}")
        return True
    
    def _record_video(self, camera_id, output_folder, filename_prefix):
        """Internal method for video recording thread"""
        try:
            cap = self.cameras[camera_id]
            
            # Get camera properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 30
            
            # Create video writer
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            filename = os.path.join(output_folder, f"{filename_prefix}_cam{camera_id}_{timestamp}.mp4")
            
            out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
            
            print(f"Recording to: {filename}")
            
            while camera_id in self.recording_threads:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    print(f"Failed to read frame from camera {camera_id}")
                    break
                    
                time.sleep(1/fps)  # Control frame rate
                
            out.release()
            print(f"Recording stopped for camera {camera_id}")
            
        except Exception as e:
            print(f"Error in recording thread for camera {camera_id}: {e}")
    
    def stop_recording(self, camera_id):
        """Stop recording for specified camera"""
        if camera_id in self.recording_threads:
            del self.recording_threads[camera_id]
            print(f"Stopped recording camera {camera_id}")
    
    def open_camera_preview(self):
        """Open preview window showing all cameras"""
        if self.preview_active:
            print("Preview already active")
            return
            
        self.preview_active = True
        self.preview_thread = threading.Thread(target=self._preview_loop)
        self.preview_thread.daemon = True
        self.preview_thread.start()
        print("Camera preview opened")
    
    def close_camera_preview(self):
        """Close preview window"""
        self.preview_active = False
        if self.preview_thread:
            self.preview_thread.join(timeout=1)
        cv2.destroyAllWindows()
        print("Camera preview closed")
    
    def _preview_loop(self):
        """Internal method for preview display"""
        try:
            while self.preview_active:
                frames = {}
                
                # Capture frames from all cameras
                for camera_id, cap in self.cameras.items():
                    ret, frame = cap.read()
                    if ret:
                        frames[camera_id] = frame
                
                if frames:
                    # Create combined preview
                    preview_frames = []
                    for camera_id in sorted(frames.keys()):
                        frame = frames[camera_id]
                        # Resize for preview
                        frame = cv2.resize(frame, (640, 480))
                        cv2.putText(frame, f"Camera {camera_id}", (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        preview_frames.append(frame)
                    
                    # Combine frames horizontally
                    if len(preview_frames) == 1:
                        combined = preview_frames[0]
                    elif len(preview_frames) == 2:
                        combined = np.hstack(preview_frames)
                    else:
                        # Stack 3 cameras in a 2x2 grid (with one empty)
                        top_row = np.hstack(preview_frames[:2])
                        bottom_row = np.hstack([preview_frames[2], np.zeros_like(preview_frames[0])])
                        combined = np.vstack([top_row, bottom_row])
                    
                    cv2.imshow("Camera Preview", combined)
                    
                    # Check for key press to close
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            print(f"Error in preview loop: {e}")
        finally:
            cv2.destroyAllWindows()
    
    def release_all(self):
        """Release all camera resources"""
        self.close_camera_preview()
        
        for camera_id in list(self.recording_threads.keys()):
            self.stop_recording(camera_id)
        
        for camera_id, cap in self.cameras.items():
            cap.release()
        
        self.cameras.clear()
        print("All cameras released")

# Global camera system instance
camera_system = CameraSystem()

# Convenience functions for main.py
def initialize_cameras():
    """Initialize all cameras (1, 2, 3)"""
    success = True
    for camera_id in [1, 2, 3]:
        if not camera_system.initialize_camera(camera_id):
            success = False
    return success

def start_recording(camera_id, output_folder):
    """Start recording for camera 2 or 3"""
    return camera_system.start_recording(camera_id, output_folder)

def capture_image(camera_id, filename, focus_value=None):
    """Capture image from camera 1"""
    return camera_system.capture_image(camera_id, filename, focus_value)

def set_camera_focus(camera_id, focus_value):
    """Set focus for camera"""
    camera_system.set_focus(camera_id, focus_value)

def open_preview():
    """Open camera preview"""
    camera_system.open_camera_preview()

def close_preview():
    """Close camera preview"""
    camera_system.close_camera_preview()

def release_cameras():
    """Release all cameras"""
    camera_system.release_all()




