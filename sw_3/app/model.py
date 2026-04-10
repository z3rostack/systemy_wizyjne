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

        self.create_identity_lut()
        self.create_lut_preview(self.lut)

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
    
    @property
    def lut(self) -> np.ndarray:
        return self._lut

    @property
    def lut_image(self) -> np.ndarray:
        return self._lut_image

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

    def transform_with_lut(self, red: bool = True, green: bool = True, blue: bool = True) -> None:
        self._right_image = self._left_image.copy()

        for ix, iy in np.ndindex(self._right_image.shape[:2]):
            b, g, r = self._right_image[ix, iy]
            if red:
                r = self._lut[r]
            if green:
                g = self._lut[g]
            if blue:
                b = self._lut[b]

            self._right_image[ix, iy] = (b, g, r)

    def create_identity_lut(self) -> np.ndarray:
        self._lut = np.arange(256, dtype=np.uint8)

    def create_negative_lut(self) -> np.ndarray:
        self._lut = np.arange(255,-1,-1, dtype=np.uint8)

    def create_brightness_lut(self, brightness: int = 0) -> np.ndarray:
        self._lut = np.clip(np.arange(256, dtype=np.int32) + brightness, 0, 255).astype(np.uint8)

    def create_threshold_lut(self, threshold: int = 128) -> np.ndarray:
        if threshold < 0 or threshold > 255:
            raise ValueError("Threshold must be in the range [0, 255].")
        
        self._lut = np.array([0 if i < threshold else 255 for i in range(256)], dtype=np.uint8)

    def create_threshold2_lut(self, thresholdA: int = 64, thresholdB: int = 192) -> np.ndarray:
        if thresholdA < 0 or thresholdA > 255 or thresholdB < 0 or thresholdB > 255:
            raise ValueError("Thresholds must be in the range [0, 255].")
        
        if thresholdA >= thresholdB:
            raise ValueError("ThresholdA must be less than ThresholdB.")
        
        self._lut = np.array([255 if thresholdA < i < thresholdB else 0 for i in range(256)], dtype=np.uint8)
        print(self._lut)

    def create_contrast_lut(self, k: int = 64) -> np.ndarray:
        if k < 0 or k > 127:
            raise ValueError("Contrast k must be in the range [0, 127].")

        l = np.full(k, 0)
        r = np.full(k, 255)

        s = 256 - 2*k
        m = np.linspace(0,255,s, dtype=np.uint8)

        a = np.concatenate((l,m,r))
        self._lut = a
        print(self._lut)

    def create_lut_preview(self, lut: list[int]) -> np.ndarray:
        lut_image = np.full((256, 256), 255, dtype=np.uint8)

        points = []
        for x, y in enumerate(self.lut):
            points.append([x, 255 - int(y)])  # invert Y

        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

        cv2.polylines(
            lut_image,
            [pts],
            isClosed=False,
            color=0,
            thickness=10,
        )

        return cv2.resize(lut_image, (64, 64))

    def _quarter_bounds(self, quarter: int) -> tuple[int, int, int, int]:
        if quarter not in (1, 2, 3, 4):
            raise ValueError("Quarter must be one of: 1, 2, 3, 4.")

        height, width = self._left_image.shape[:2]
        half_height = height // 2
        half_width = width // 2

        if quarter == 1:
            return 0, half_height, 0, half_width
        if quarter == 2:
            return 0, half_height, half_width, width
        if quarter == 3:
            return half_height, height, 0, half_width

        return half_height, height, half_width, width

    def zoom_in(self, quarter: int) -> np.ndarray:
        y0, y1, x0, x1 = self._quarter_bounds(quarter)
        roi = self._left_image[y0:y1, x0:x1]

        zoomed = np.repeat(np.repeat(roi, 2, axis=0), 2, axis=1)
        self._right_image = zoomed[:IMAGE_HEIGHT, :IMAGE_WIDTH].copy()
        return self._right_image

    def zoom_out(self, quarter: int) -> np.ndarray:
        self._quarter_bounds(quarter)

        downsampled = self._left_image[::2, ::2]
        half_height, half_width = downsampled.shape[:2]

        result = self.create_blank_image()

        if quarter == 1:
            y0, x0 = 0, 0
        elif quarter == 2:
            y0, x0 = 0, IMAGE_WIDTH - half_width
        elif quarter == 3:
            y0, x0 = IMAGE_HEIGHT - half_height, 0
        else:
            y0, x0 = IMAGE_HEIGHT - half_height, IMAGE_WIDTH - half_width

        result[y0:y0 + half_height, x0:x0 + half_width] = downsampled
        self._right_image = result
        return self._right_image