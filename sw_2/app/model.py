from __future__ import annotations

import cv2
import numpy as np

from app.constants import CHANNELS, IMAGE_HEIGHT, IMAGE_WIDTH, LINE_IMAGE_HEIGHT


class ImageModel:
    """Encapsulates image state and OpenCV operations."""

    def __init__(self) -> None:
        self._left_image = self.create_blank_image()
        self._right_image = self.create_blank_image()

        self._left_line_image = self.create_blank_line_image()
        self._right_line_image = self.create_blank_line_image()

    @property
    def left_image(self) -> np.ndarray:
        return self._left_image

    @property
    def left_line_image(self) -> np.ndarray:
        return self._left_line_image

    @property
    def right_image(self) -> np.ndarray:
        return self._right_image

    @property
    def right_line_image(self) -> np.ndarray:
        return self._right_line_image

    def create_blank_image(self) -> np.ndarray:
        return np.full((IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS), 0, dtype=np.uint8)

    def create_blank_line_image(self) -> np.ndarray:
        return np.full((LINE_IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS), 0, dtype=np.uint8)

    def clear(self) -> None:
        self._left_image = self.create_blank_image()

    def clear_right(self) -> None:
        self._right_image = self.create_blank_image()

    def load_left_from_file(self, path: str) -> np.ndarray:
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Could not load image from: {path}")

        self._left_image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT))
        return self._left_image

    def load_right_from_file(self, path: str) -> np.ndarray:
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Could not load image from: {path}")

        self._right_image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT))
        return self._right_image

    def capture_left_from_camera(self, camera_index: int = 0) -> np.ndarray:
        camera = cv2.VideoCapture(camera_index)
        if not camera.isOpened():
            raise RuntimeError("Cannot open camera.")

        try:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Cannot receive frame from camera.")
        finally:
            camera.release()

        self._left_image = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
        return self._left_image

    def capture_right_from_camera(self, camera_index: int = 0) -> np.ndarray:
        camera = cv2.VideoCapture(camera_index)
        if not camera.isOpened():
            raise RuntimeError("Cannot open camera.")

        try:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Cannot receive frame from camera.")
        finally:
            camera.release()

        self._right_image = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
        return self._right_image

    def draw_left_rectangles(self) -> np.ndarray:
        image = self._left_image.copy()
        cv2.rectangle(image, (40, 40), (360, 260), (255, 0, 0), thickness=1)
        cv2.rectangle(image, (120, 100), (280, 200), (0, 255, 0), thickness=1)
        self._left_image = image
        return self._left_image

    def draw_right_rectangles(self) -> np.ndarray:
        image = self._right_image.copy()
        cv2.rectangle(image, (40, 40), (360, 260), (255, 0, 0), thickness=1)
        cv2.rectangle(image, (120, 100), (280, 200), (0, 255, 0), thickness=1)
        self._right_image = image
        return self._right_image

    def copy_to_right(self, red: bool = True, green: bool = True, blue: bool = True) -> np.ndarray:
        self._right_image = self.rgb_select(
            self._left_image.copy(), red, green, blue)
        return self._right_image

    def copy_to_left(self, red: bool = True, green: bool = True, blue: bool = True) -> np.ndarray:
        self._left_image = self.rgb_select(
            self._right_image.copy(), red, green, blue)
        return self._left_image

    def rgb_select(self, image, red: bool = True, green: bool = True, blue: bool = True) -> np.ndarray:
        if not red:
            image[:, :, 2] = 0
        if not green:
            image[:, :, 1] = 0
        if not blue:
            image[:, :, 0] = 0
        return image

    def grayscale_to_right(self) -> np.ndarray:
        for ix, iy in np.ndindex(self._left_image.shape[:2]):
            r, g, b = self._left_image[ix, iy]
            gray = (r // 3 + g // 3 + b // 3)
            self._right_image[ix, iy] = (gray, gray, gray)
        return self._right_image

    def get_rgb_values(self, x: int, y: int) -> tuple[int, int, int]:
        if 0 <= x < self._left_image.shape[1] and 0 <= y < self._left_image.shape[0]:
            b, g, r = self._left_image[y, x]
            return r, g, b
        else:
            raise ValueError("Coordinates are out of bounds.")

    def _get_line(self, height, image) -> np.ndarray:
        line_image = np.full((LINE_IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS), 0, dtype=np.uint8)
        line = image[height, :, :]

        for i in np.arange(line.shape[0]):
            vals = (255 - line[i, :]) // 2
            line_image[vals[2], i] = np.add(
                line_image[vals[2], i], (0, 0, 255))
            line_image[vals[1], i] = np.add(
                line_image[vals[1], i], (0, 255, 0))
            line_image[vals[0], i] = np.add(
                line_image[vals[0], i], (255, 0, 0))

        return line_image

    def draw_left_line(self, height: int):
        self._left_line_image = self._get_line(height, self._left_image)

    def draw_right_line(self, height: int):
        self._right_line_image = self._get_line(height, self._right_image)
