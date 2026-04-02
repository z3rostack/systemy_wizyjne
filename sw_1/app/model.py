from __future__ import annotations

import cv2
import numpy as np


class ImageModel:
    """Encapsulates image state and OpenCV operations."""

    def __init__(self) -> None:
        self._image = self.create_blank_image()

    @property
    def image(self) -> np.ndarray:
        return self._image

    def create_blank_image(self) -> np.ndarray:
        return np.full((240, 320, 3), 255, dtype=np.uint8)

    def clear(self) -> None:
        self._image = self.create_blank_image()

    def load_from_file(self, path: str) -> np.ndarray:
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Could not load image from: {path}")

        self._image = cv2.resize(image, (320, 240))
        return self._image

    def capture_from_camera(self, camera_index: int = 0) -> np.ndarray:
        camera = cv2.VideoCapture(camera_index)
        if not camera.isOpened():
            raise RuntimeError("Cannot open camera.")

        try:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Cannot receive frame from camera.")
        finally:
            camera.release()

        self._image = cv2.resize(frame, (320, 240))
        return self._image

    def draw_rectangles(self) -> np.ndarray:
        image = self._image.copy()
        cv2.rectangle(image, (40, 40), (300, 180), (255, 0, 0), thickness=1)
        cv2.rectangle(image, (120, 100), (280, 200), (0, 255, 0), thickness=1)
        self._image = image
        return self._image
