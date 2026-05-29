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

    def draw_shape(self, image: np.ndarray):
        cv2.rectangle(image, (110, 70), (210, 170), (255, 0, 0), 5)
        cv2.circle(image, (160, 120), 50, (0, 255, 0), 5)
        cv2.line(image, (110, 70), (210, 170), (0, 0, 255), 5)

    def draw_image( self, side: str):
        if side == self.LEFT:
            self.draw_shape(self._left_image)
        elif side == self.RIGHT:
            self.draw_shape(self._right_image)
        else:
            raise ValueError(f"Invalid side: {side}")

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

    def gen_matrix(self, type: list) -> np.ndarray:
        match type:
            case "low_pass":
                return np.array([[1, 1, 1],
                                 [1, 1, 1],
                                 [1, 1, 1]])
            case "high_pass":
                return np.array([[-1, -1, -1],
                                 [-1, 9, -1],
                                 [-1, -1, -1]])
            case "prewit":
                return np.array([[-1, -1, -1],
                                 [0, 0, 0],
                                 [1, 1, 1]])
            case "sobel":
                return np.array([[1, 2, 1],
                                 [0, 0, 0],
                                 [-1, -2, -1]])
            case "gaussian":
                return np.array([[1, 2, 1],
                                 [2, 4, 2],
                                 [1, 2, 1]])
            case "laplace":
                return np.array([[0, 1, 0],
                                 [1, -4, 1],
                                 [0, 1, 0]])
            case _:
                raise ValueError(f"Invalid matrix type: {type}")

    def matrix_filter(self, matrix: np.ndarray, kernel: np.ndarray):
        matrix = matrix.astype(np.float32)
        kernel = kernel.astype(np.float32)

        h, w = np.shape(matrix)
        sum_weight = 0.0
        sum_output = 0.0

        for y in range(h):
            for x in range(w):
                sum_weight += kernel[y,x]
                sum_output += matrix[y,x] * kernel[y,x]

        output = 0.0
        if sum_weight != 0.0:
            output = sum_output / sum_weight
        else:
            output = sum_output

        output = np.clip(output, 0, 255)
        return np.uint8(output)

    def filter_buffer2_opencv(self, kernel: np.ndarray, equalize: bool = False):
        sum = kernel.sum()
        if sum != 0:
            kernel = kernel / sum

        print(f"Kernel:\n{kernel}")

        image = self._buffer2.copy()

        image = cv2.filter2D(image, -1, kernel)

        if equalize:
            image = image // 2
            image += 128

        self._buffer3 = image

    def filter_buffer2(self, kernel: np.ndarray, equalize: bool = False):
        input_image = self._buffer2.copy()
        output_image = self._create_blank_image()

        h, w, c = np.shape(input_image)

        for y in range(h-2):
            for x in range(w-2):
                for ch in range(c):
                    sub = input_image[y:y+3, x:x+3, ch]
                    output_image[y+1, x+1, ch] = self.matrix_filter(sub, kernel)

        if equalize:
            output_image = output_image // 2
            output_image += 128

        self._buffer3 = output_image


    def to_grayscale(self):
        b, g, r = self._buffer2[:,:,0], self._buffer2[:,:,1], self._buffer2[:,:,2]
        grayscale = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
        self._buffer3 = np.stack([grayscale, grayscale, grayscale], axis=2)

    def dilate_buffer2(self):        
        input_image = self._buffer2.copy()
        output_image = self._buffer2.copy()

        h, w, c = np.shape(input_image)

        for y in range(h-2):
            for x in range(w-2):
                for ch in range(c):
                    sub = input_image[y:y+3, x:x+3, ch]
                    output_image[y+1, x+1, ch] = np.max(sub)

        self._buffer3 = output_image

    def erode_buffer2(self):
        input_image = self._buffer2.copy()
        output_image = self._buffer2.copy()

        h, w, c = np.shape(input_image)

        for y in range(h-2):
            for x in range(w-2):
                for ch in range(c):
                    sub = input_image[y:y+3, x:x+3, ch]
                    output_image[y+1, x+1, ch] = np.min(sub)

        self._buffer3 = output_image

    def color_threshold_buffer2(self, r_lthreshold: int = 0, r_uthreshold: int = 255, g_lthreshold: int = 0, g_uthreshold: int = 255, b_lthreshold: int = 0, b_uthreshold: int = 255):
            input_image = self._buffer2.copy()
            output_image = self._buffer2.copy()
    
            h, w, _ = np.shape(input_image)
    
            for y in range(h):
                for x in range(w):
                    b, g, r = input_image[y,x]
                    if r_lthreshold <= r <= r_uthreshold and g_lthreshold <= g <= g_uthreshold and b_lthreshold <= b <= b_uthreshold:
                        output_image[y,x] = [255, 255, 255]
                    else:
                        output_image[y,x] = [0, 0, 0]
    
            self._buffer3 = output_image

    def open_buffer2(self):
        pass

    def close_buffer2(self):
        pass
