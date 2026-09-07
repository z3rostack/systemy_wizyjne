from collections import deque

import cv2
import numpy as np


class Model:
    IMAGE_WIDTH = 640
    IMAGE_HEIGHT = 480

    def __init__(self) -> None:
        self.image = self._blank_image()
        self.flammable_color = np.array([255, 255, 255], dtype=np.uint8)
        self.scorch_color = np.array([0, 0, 0], dtype=np.uint8)
        self.smoldering_color = np.array([51, 153, 255], dtype=np.uint8)
        self.burning_color = np.array([0, 0, 204], dtype=np.uint8)
        self.scorched_color = np.array([51, 204, 51], dtype=np.uint8)
        self.burnt_color = np.array([100, 100, 100], dtype=np.uint8)
        self.diagonal_neighbors = False
        self._smoldering: deque[tuple[int, int]] = deque()
        self._burning: deque[tuple[int, int]] = deque()
        self._scorched: set[tuple[int, int]] = set()
        self._burnt: set[tuple[int, int]] = set()

    def _blank_image(self) -> np.ndarray:
        return np.zeros((self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3), dtype=np.uint8)

    def clear(self) -> None:
        self.image = self._blank_image()
        self.reset_fire()

    def load_image(self, path: str) -> None:
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Cannot open image: {path}")
        self.image = cv2.resize(image, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        self.reset_fire()

    def reset_fire(self) -> None:
        self._smoldering.clear()
        self._burning.clear()
        self._scorched.clear()
        self._burnt.clear()

    def pixel(self, x: int, y: int) -> tuple[int, int, int]:
        if not (0 <= x < self.IMAGE_WIDTH and 0 <= y < self.IMAGE_HEIGHT):
            raise ValueError("Pixel is outside the image")
        blue, green, red = self.image[y, x]
        return int(red), int(green), int(blue)

    def ignite(self, x: int, y: int) -> None:
        if self._in_bounds(x, y) and np.array_equal(self.image[y, x], self.flammable_color):
            self._smoldering.append((x, y))
            self.image[y, x] = self.smoldering_color

    def burn_step(self) -> None:
        while self._smoldering:
            point = self._smoldering.popleft()
            self._burning.append(point)
            self.image[point[1], point[0]] = self.burning_color

        current_burning = list(self._burning)
        for x, y in current_burning:
            for neighbor_x, neighbor_y in self._neighbors(x, y):
                pixel = self.image[neighbor_y, neighbor_x]
                if np.array_equal(pixel, self.flammable_color):
                    self._smoldering.append((neighbor_x, neighbor_y))
                    self.image[neighbor_y, neighbor_x] = self.smoldering_color
                elif np.array_equal(pixel, self.scorch_color):
                    self._scorched.add((neighbor_x, neighbor_y))
                    self.image[neighbor_y, neighbor_x] = self.scorched_color

        while self._burning:
            point = self._burning.popleft()
            self._burnt.add(point)
            self.image[point[1], point[0]] = self.burnt_color

    def burn_all(self) -> None:
        while self._smoldering or self._burning:
            self.burn_step()

    def fire_counts(self) -> tuple[int, int, int, int]:
        return (len(self._smoldering), len(self._burning), len(self._scorched), len(self._burnt))

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 < x < self.IMAGE_WIDTH - 1 and 0 < y < self.IMAGE_HEIGHT - 1

    def _neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        if self.diagonal_neighbors:
            neighbors.extend(((x - 1, y - 1), (x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1)))
        return [point for point in neighbors if self._in_bounds(*point)]
