from collections import deque
import math

import cv2
import numpy as np


class Model:
    IMAGE_WIDTH = 320
    IMAGE_HEIGHT = 240

    def __init__(self) -> None:
        self.image = self._blank_image()
        self.objects_image = self._blank_image()
        self.mechanic_image = self._blank_image()

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
        self._objects: list[set[tuple[int, int]]] = []
        self.mechanic_data: dict[str, float] = {}

    def _blank_image(self) -> np.ndarray:
        """Return a new black buffer of the working image size."""
        return np.zeros((self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3), dtype=np.uint8)

    def clear(self) -> None:
        """Reset all three buffers to black and drop the fire state."""
        self.image = self._blank_image()
        self.objects_image = self._blank_image()
        self.mechanic_image = self._blank_image()

        self.reset_fire()

    def load_image(self, path: str) -> None:
        """Load an image from disk, scaled to the buffer size. Raises ValueError if it cannot be read."""
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Cannot open image: {path}")
        # nearest neighbour keeps the colors exact, so flammable/scorch pixels stay recognizable
        self.image = cv2.resize(image, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT),
                                interpolation=cv2.INTER_NEAREST)
        self.reset_fire()

    def reset_fire(self) -> None:
        """Clear the fire queues, counters and the segmented objects."""
        self._smoldering.clear()
        self._burning.clear()
        self._scorched.clear()
        self._burnt.clear()
        self._objects.clear()

    def pixel(self, x: int, y: int) -> tuple[int, int, int]:
        """Return the (red, green, blue) value of one pixel. Raises ValueError outside the image."""
        if not (0 <= x < self.IMAGE_WIDTH and 0 <= y < self.IMAGE_HEIGHT):
            raise ValueError("Pixel is outside the image")
        blue, green, red = self.image[y, x]
        return int(red), int(green), int(blue)

    def ignite(self, x: int, y: int) -> None:
        """Start a fire at the given pixel, if it is flammable."""
        if self._in_bounds(x, y) and np.array_equal(self.image[y, x], self.flammable_color):
            self._smoldering.append((x, y))
            self.image[y, x] = self.smoldering_color

    def burn_step(self) -> None:
        """Advance the fire by one generation: burning pixels burn out, smoldering ones catch fire and spread."""
        while self._burning:
            point = self._burning.popleft()
            self._burnt.add(point)
            self.image[point[1], point[0]] = self.burnt_color

        while self._smoldering:
            point = self._smoldering.popleft()
            self._burning.append(point)
            self.image[point[1], point[0]] = self.burning_color

        for x, y in self._burning:
            for neighbor_x, neighbor_y in self._neighbors(x, y):
                pixel = self.image[neighbor_y, neighbor_x]
                if np.array_equal(pixel, self.flammable_color):
                    self._smoldering.append((neighbor_x, neighbor_y))
                    self.image[neighbor_y, neighbor_x] = self.smoldering_color
                elif np.array_equal(pixel, self.scorch_color):
                    self._scorched.add((neighbor_x, neighbor_y))
                    self.image[neighbor_y, neighbor_x] = self.scorched_color

    @property
    def is_burning(self) -> bool:
        """Tell whether any pixel is still smoldering or burning."""
        return bool(self._smoldering or self._burning)

    def burn_cycle(self) -> None:
        """Run burn steps until the current region is completely burnt out."""
        while self._smoldering or self._burning:
            self.burn_step()

    def burn_all(self) -> None:
        """Segment the buffer by burning every flammable region as a separate numbered object."""
        self.reset_fire()
        seed = self._find_flammable_pixel()
        while seed is not None:
            burnt_before = set(self._burnt)
            self.ignite(*seed)
            self.burn_cycle()
            pixels = self._burnt - burnt_before
            self._objects.append(pixels)
            self._paint(pixels, self._object_color(len(self._objects)))
            seed = self._find_flammable_pixel()

    def mechanic_analysis(self) -> np.ndarray:
        """Measure the shown object (area, centroid, moments, principal axes, length).

        Returns the annotated image and fills mechanic_data. Raises ValueError when no object is shown.
        """
        image = self.objects_image.copy()
        # cut off the object where it touches the image border
        cv2.rectangle(image, (0, 0), (self.IMAGE_WIDTH - 1, self.IMAGE_HEIGHT - 1), (0, 0, 0), 2)

        ys, xs = np.nonzero(np.all(image == 255, axis=2))
        area = float(xs.size)
        if area == 0:
            raise ValueError("Show an object before running the mechanic analysis")

        xs = xs.astype(float)
        ys = ys.astype(float)
        x0 = xs.sum() / area
        y0 = ys.sum() / area

        jx0 = float((ys**2).sum()) - area * y0**2
        jy0 = float((xs**2).sum()) - area * x0**2
        jx0y0 = float((xs * ys).sum()) - area * x0 * y0

        radius = math.sqrt(0.25 * (jy0 - jx0) ** 2 + jx0y0**2)
        je_0 = (jx0 + jy0) / 2 + radius
        jt_0 = (jx0 + jy0) / 2 - radius

        alfa_e = math.atan(jx0y0 / (jy0 - je_0)) if jy0 != je_0 else math.pi / 2
        alfa_t = math.atan(jx0y0 / (jy0 - jt_0)) if jy0 != jt_0 else math.pi / 2
        e_vector = (math.cos(alfa_e), math.sin(alfa_e))
        t_vector = (math.cos(alfa_t), math.sin(alfa_t))

        center = (int(x0), int(y0))
        e_ends = (self._find_edge(image, center, e_vector),
                  self._find_edge(image, center, (-e_vector[0], -e_vector[1])))
        t_ends = (self._find_edge(image, center, t_vector),
                  self._find_edge(image, center, (-t_vector[0], -t_vector[1])))
        length = max(self._distance(*e_ends), self._distance(*t_ends))

        # drawn after the edge search so the outline is not mistaken for the object border
        top_left = (int(xs.min()), int(ys.min()))
        bottom_right = (int(xs.max()), int(ys.max()))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 255), 2)

        for point in e_ends:
            if point is not None:
                cv2.circle(image, point, 6, (0, 0, 255), 2)
        for point in t_ends:
            if point is not None:
                cv2.circle(image, point, 6, (255, 0, 0), 2)

        cv2.circle(image, center, 6, (255, 0, 0), 2)
        cv2.line(image, center, (center[0] + 120, center[1]), (0, 255, 0), 2)
        cv2.line(image, center, self._offset(center, e_vector, 100), (0, 0, 255), 2)
        cv2.line(image, center, self._offset(center, t_vector, 100), (255, 0, 0), 2)

        self.mechanic_image = image
        self.mechanic_data = {
            "Area": area,
            "Center X": x0,
            "Center Y": y0,
            "Jx0": jx0,
            "Jy0": jy0,
            "Jx0y0": jx0y0,
            "Je_0": je_0,
            "Jt_0": jt_0,
            "Alfa e [deg]": math.degrees(alfa_e),
            "Alfa t [deg]": math.degrees(alfa_t),
            "Length": length,
        }
        return self.mechanic_image

    @property
    def object_count(self) -> int:
        """Number of objects found by the last burn_all call."""
        return len(self._objects)

    def object_image(self, number: int) -> np.ndarray:
        """Return the selected object drawn white on black. Raises ValueError for an unknown number."""
        if not 1 <= number <= len(self._objects):
            raise ValueError(f"There is no object number {number}")
        image = self._blank_image()
        for x, y in self._objects[number - 1]:
            image[y, x] = (255, 255, 255)
        self.objects_image = image
        return image

    def fire_counts(self) -> tuple[int, int, int, int]:
        """Return the number of smoldering, burning, scorched and burnt pixels."""
        return (len(self._smoldering), len(self._burning), len(self._scorched), len(self._burnt))

    def _find_flammable_pixel(self) -> tuple[int, int] | None:
        """Return the first flammable pixel outside the border, or None when none is left."""
        mask = np.all(self.image == self.flammable_color, axis=2)
        mask[0, :] = mask[-1, :] = False
        mask[:, 0] = mask[:, -1] = False
        found = np.argwhere(mask)
        if found.size == 0:
            return None
        y, x = found[0]
        return int(x), int(y)

    def _object_color(self, number: int) -> np.ndarray:
        """Return the burnt shade that marks the object with the given number."""
        return np.clip(self.burnt_color.astype(int) + number, 0, 255).astype(np.uint8)

    def _offset(self, center: tuple[int, int], vector: tuple[float, float], scale: float) -> tuple[int, int]:
        """Return the integer point lying scale pixels from center along vector."""
        return int(center[0] + scale * vector[0]), int(center[1] + scale * vector[1])

    def _find_edge(self, image: np.ndarray, center: tuple[int, int],
                   vector: tuple[float, float], max_range: int = 320) -> tuple[int, int] | None:
        """Walk from center along vector and return the first black pixel, or None if there is none."""
        for step in range(1, max_range):
            x, y = self._offset(center, vector, step)
            if not (0 <= x < self.IMAGE_WIDTH and 0 <= y < self.IMAGE_HEIGHT):
                return None
            if image[y, x, 0] == 0:
                return x, y
        return None

    def _distance(self, start: tuple[int, int] | None, end: tuple[int, int] | None) -> float:
        """Return the distance between two points, or 0 when either one is missing."""
        if start is None or end is None:
            return 0.0
        return math.dist(start, end)

    def _paint(self, pixels: set[tuple[int, int]], color: np.ndarray) -> None:
        """Fill the given pixels of the main image with one color."""
        for x, y in pixels:
            self.image[y, x] = color

    def _in_bounds(self, x: int, y: int) -> bool:
        """Tell whether the pixel lies inside the image, excluding the outermost row and column."""
        return 0 < x < self.IMAGE_WIDTH - 1 and 0 < y < self.IMAGE_HEIGHT - 1

    def _neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return the 4 neighbours of a pixel, or 8 when diagonal_neighbors is on."""
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        if self.diagonal_neighbors:
            neighbors.extend(((x - 1, y - 1), (x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1)))
        return [point for point in neighbors if self._in_bounds(*point)]
