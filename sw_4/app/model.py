import cv2
import numpy as np

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
CHANNELS = 3

class Model:
    LEFT = "left"
    RIGHT = "right"
    BUFFER1 = "buffer1"
    BUFFER2 = "buffer2"
    BUFFER3 = "buffer3"

    AND = "AND"
    OR = "OR"
    XOR = "XOR"

    _left_image = None
    _right_image = None

    _buffer1 = None
    _buffer2 = None
    _buffer3 = None

    @property
    def left_image(self):
        return self._left_image
    
    @property
    def right_image(self):
        return self._right_image
    
    @property
    def buffer1(self):
        return self._buffer1

    @property
    def buffer2(self):
        return self._buffer2

    @property
    def buffer3(self):
        return self._buffer3

    def __init__(self):
        self.data = "Hello from Model!"

        self._left_image = self._create_blank_image()
        self._right_image = self._create_blank_image()

        self._buffer1 = self._create_blank_image()
        self._buffer2 = self._create_blank_image()
        self._buffer3 = self._create_blank_image()

    def _load_from_file(self, path: str) -> np.ndarray:
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Could not load image from: {path}")

        image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT))
        return image

    def _capture_from_camera(self, camera_index: int = 0) -> np.ndarray:
        camera = cv2.VideoCapture(camera_index)
        if not camera.isOpened():
            raise RuntimeError("Cannot open camera.")

        try:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Cannot receive frame from camera.")
        finally:
            camera.release()

        image = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
        return image

    def _create_blank_image(self) -> np.ndarray:
        return np.full((IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS), 0, dtype=np.uint8)
    
    def clear_left_image(self):
        self._left_image = self._create_blank_image()

    def clear_right_image(self):
        self._right_image = self._create_blank_image()
    
    def load_left_image_from_file(self, path: str):
        self._left_image = self._load_from_file(path)

    def load_right_image_from_file(self, path: str):
        self._right_image = self._load_from_file(path)

    def capture_left_image_from_camera(self, camera_index: int = 0):
        self._left_image = self._capture_from_camera(camera_index)

    def capture_right_image_from_camera(self, camera_index: int = 0):
        self._right_image = self._capture_from_camera(camera_index)

    def copy_buf(self, src: str, dst: str):

        match src:
            case self.LEFT:
                source_image = self._left_image
            case self.RIGHT:
                source_image = self._right_image
            case self.BUFFER1:
                source_image = self._buffer1
            case self.BUFFER2:
                source_image = self._buffer2
            case self.BUFFER3:
                source_image = self._buffer3
            case _:
                raise ValueError(f"Invalid source: {src}")
            
        match dst:
            case self.LEFT:
                self._left_image = source_image.copy()
            case self.RIGHT:
                self._right_image = source_image.copy()
            case self.BUFFER1:
                self._buffer1 = source_image.copy()
            case self.BUFFER2:
                self._buffer2 = source_image.copy()
            case self.BUFFER3:
                self._buffer3 = source_image.copy()
            case _:
                raise ValueError(f"Invalid destination: {dst}")
            
    def transform(self, operation: str):
        match operation:
            case self.AND:
                self._buffer3 = cv2.bitwise_and(self._buffer1, self._buffer2)
            case self.OR:
                self._buffer3 = cv2.bitwise_or(self._buffer1, self._buffer2)
            case self.XOR:
                self._buffer3 = cv2.bitwise_xor(self._buffer1, self._buffer2)
            case _:
                raise ValueError(f"Invalid operation: {operation}")
            

    def low_pass_matrix(self) -> np.ndarray:
        return np.array([[1, 1, 1],
                         [1, 0, 1],
                         [1, 1, 1]])
    
    def high_pass_matrix(self) -> np.ndarray:
        return np.array([[0, -1, 0],
                            [-1, 4, -1],
                            [0, -1, 0]])
        
    def filter_buffer2(self, kernel: np.ndarray):
        self._buffer3 = cv2.filter2D(self._buffer2, -1, kernel)

    def threshold_buffer2(self, threshold: int = 128):
        _, self._buffer3 = cv2.threshold(self._buffer2, threshold, 255, cv2.THRESH_BINARY)
            
    def dilate_buffer2(self):
        self._buffer3 = cv2.dilate(self._buffer2, None, iterations=1)

    def erode_buffer2(self):
        self._buffer3 = cv2.erode(self._buffer2, None, iterations=1)