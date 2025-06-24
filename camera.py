import cv2
import numpy as np
import os

# Example usage:
# cam0 = Camera(camera_id=0)
# cam1 = Camera(camera_id=1)
# cam0.calibrate()
# cam1.calibrate()
# frame0 = cam0.read()
# frame1 = cam1.read()
# cam0.release()
# cam1.release()


class Camera:
    def __init__(self, camera_id=0, calibration_file=None):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        self.calibration_file = calibration_file or f"camera_{camera_id}_calibration.npz"
        self.mtx = None
        self.dist = None
        if os.path.exists(self.calibration_file):
            self.load_calibration()

    def calibrate(self, chessboard_size=(9,6), square_size=1.0):
        """
        Calibrate the camera using chessboard images.
        chessboard_size: (columns, rows) of inner corners.
        square_size: size of a square in your defined unit (e.g., millimeters).
        """
        objp = np.zeros((chessboard_size[1]*chessboard_size[0],3), np.float32)
        objp[:,:2] = np.mgrid[0:chessboard_size[0],0:chessboard_size[1]].T.reshape(-1,2)
        objp *= square_size

        objpoints = []
        imgpoints = []

        print(f"Camera {self.camera_id}: Press SPACE to capture chessboard images. Press ESC when done.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
            display = frame.copy()
            if found:
                cv2.drawChessboardCorners(display, chessboard_size, corners, found)
            cv2.imshow(f'Calibration Camera {self.camera_id}', display)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
            elif key == 32 and found:  # SPACE
                objpoints.append(objp)
                imgpoints.append(corners)
                print(f"Captured image {len(objpoints)}")

        cv2.destroyAllWindows()

        if len(objpoints) < 5:
            print("Not enough images for calibration.")
            return False

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)
        np.savez(self.calibration_file, mtx=mtx, dist=dist)
        self.mtx = mtx
        self.dist = dist
        print(f"Calibration complete. Saved to {self.calibration_file}")
        return True

    def load_calibration(self):
        if not os.path.exists(self.calibration_file):
            raise FileNotFoundError(f"Calibration file {self.calibration_file} not found. Please calibrate first.")
        data = np.load(self.calibration_file)
        self.mtx = data['mtx']
        self.dist = data['dist']

    def undistort(self, frame):
        if self.mtx is None or self.dist is None:
            raise ValueError("Camera is not calibrated. Please calibrate or load calibration first.")
        return cv2.undistort(frame, self.mtx, self.dist, None, self.mtx)

    def read(self, undistort=True):
        ret, frame = self.cap.read()
        if not ret:
            return None
        if undistort and self.mtx is not None and self.dist is not None:
            frame = self.undistort(frame)
        return frame

    def release(self):
        self.cap.release()

def Capture(camera_id=0, filename="capture.png", undistort=True):
    """
    Capture a photograph from the specified camera and save it to a file.
    """
    cam = Camera(camera_id=camera_id)
    # Try to set to a high resolution (modify as needed for your camera)
    for width, height in [(3840,2160), (1920,1080), (1280,720)]:
        cam.cap.set(3, width)
        cam.cap.set(4, height)
        actual_width = cam.cap.get(3)
        actual_height = cam.cap.get(4)
        if actual_width == width and actual_height == height:
            break

    frame = cam.read(undistort=undistort)
    if frame is not None:
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
    else:
        print("Failed to capture image.")
    cam.release()

def RecordVideo(camera_id=0, filename="capture.avi", duration=5, fps=30, undistort=True):
    """
    Record a video from the specified camera and save it to a file.
    duration: seconds to record
    fps: frames per second
    """
    cam = Camera(camera_id=camera_id)
    # Try to set to a high resolution (modify as needed for your camera)
    for width, height in [(3840,2160), (1920,1080), (1280,720)]:
        cam.cap.set(3, width)
        cam.cap.set(4, height)
        actual_width = int(cam.cap.get(3))
        actual_height = int(cam.cap.get(4))
        if actual_width == width and actual_height == height:
            break

    # Use the actual resolution
    frame_width = int(cam.cap.get(3))
    frame_height = int(cam.cap.get(4))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

    frame_count = int(duration * fps)
    for _ in range(frame_count):
        frame = cam.read(undistort=undistort)
        if frame is not None:
            out.write(frame)
        else:
            print("Frame capture failed.")
            break

    out.release()
    cam.release()
    print(f"Video saved as {filename}")

