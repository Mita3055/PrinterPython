"""Camera interface for 48MP ELP USB camera on Raspberry Pi using OpenCV."""

import cv2
import time


class ELPCamera:
    """Simple wrapper around :class:`cv2.VideoCapture` for the ELP USB camera."""

    def __init__(self, camera_index: int = 0, width: int = 8000, height: int = 6000, fps: int = 10):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None

    def open(self, autofocus: bool = True) -> bool:
        """Open the USB camera and configure capture settings."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Unable to open ELP USB camera")

        # Set resolution and frame rate
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.width))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.height))
        self.cap.set(cv2.CAP_PROP_FPS, float(self.fps))

        # Enable autofocus if available
        if autofocus and hasattr(cv2, "CAP_PROP_AUTOFOCUS"):
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

        # Give the camera a moment to adjust
        time.sleep(2)
        return True

    def read(self):
        """Read a single frame from the camera."""
        if self.cap is None:
            raise RuntimeError("Camera is not opened")
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera")
        return frame

    def close(self):
        """Release the camera resource."""
        if self.cap:
            self.cap.release()
            self.cap = None


def TakePicture(filename: str = "elp_capture.jpg", camera_index: int = 0) -> str:
    """Capture a single photo with autofocus and save it.

    Args:
        filename: Path to save the captured image.
        camera_index: Index of the camera device.

    Returns:
        The path to the saved image.
    """
    cam = ELPCamera(camera_index)
    cam.open(autofocus=True)
    frame = cam.read()
    cv2.imwrite(filename, frame)
    cam.close()
    return filename


if __name__ == "__main__":
    # Example usage
    path = TakePicture()
    print(f"Image saved as {path}")
