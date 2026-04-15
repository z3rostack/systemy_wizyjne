from app.view import MainWindowView
from app.model import Model

class MainWindowPresenter:
    def __init__(self, view: MainWindowView, model: Model):
        self.view = view
        self.model = model

        # Setup slots
        self.view.view.left_file_image.clicked.connect(self.load_left_image)
        self.view.view.right_file_image.clicked.connect(self.load_right_image)

        self.view.view.left_clear_image.clicked.connect(self.clear_left_image)
        self.view.view.right_clear_image.clicked.connect(self.clear_right_image)

        self.view.view.left_camera_image.clicked.connect(self.load_left_image_from_camera)
        self.view.view.right_camera_image.clicked.connect(self.load_right_image_from_camera)

        self.view.view.left_to_buf1.clicked.connect(lambda: self.copy_buf(self.model.LEFT, self.model.BUFFER1))
        self.view.view.buf1_to_left.clicked.connect(lambda: self.copy_buf(self.model.BUFFER1, self.model.LEFT))
        self.view.view.left_to_buf2.clicked.connect(lambda: self.copy_buf(self.model.LEFT, self.model.BUFFER2))
        self.view.view.buf2_to_left.clicked.connect(lambda: self.copy_buf(self.model.BUFFER2, self.model.LEFT))
        self.view.view.left_to_buf3.clicked.connect(lambda: self.copy_buf(self.model.LEFT, self.model.BUFFER3))
        self.view.view.buf3_to_left.clicked.connect(lambda: self.copy_buf(self.model.BUFFER3, self.model.LEFT))

        self.view.view.right_to_buf1.clicked.connect(lambda: self.copy_buf(self.model.RIGHT, self.model.BUFFER1))
        self.view.view.buf1_to_right.clicked.connect(lambda: self.copy_buf(self.model.BUFFER1, self.model.RIGHT))
        self.view.view.right_to_buf2.clicked.connect(lambda: self.copy_buf(self.model.RIGHT, self.model.BUFFER2))
        self.view.view.buf2_to_right.clicked.connect(lambda: self.copy_buf(self.model.BUFFER2, self.model.RIGHT))
        self.view.view.right_to_buf3.clicked.connect(lambda: self.copy_buf(self.model.RIGHT, self.model.BUFFER3))
        self.view.view.buf3_to_right.clicked.connect(lambda: self.copy_buf(self.model.BUFFER3, self.model.RIGHT))

        self.view.view.transform_button.clicked.connect(self.transform)

        self.view.view.low_pass_button.clicked.connect(self.low_pass)
        self.view.view.high_pass_button.clicked.connect(self.high_pass)
        self.view.view.filter_button.clicked.connect(self.filter)
        self.view.view.threshold_button.clicked.connect(self.threshold)
        self.view.view.dilate_button.clicked.connect(self.dilate)
        self.view.view.erode_button.clicked.connect(self.erode)

    def clear_left_image(self):
        self.model.clear_left_image()
        self.view.set_left_image(self.model.left_image)

    def clear_right_image(self):    
        self.model.clear_right_image()
        self.view.set_right_image(self.model.right_image)

    def load_left_image(self):
        path = self.view.prompt_for_image_path()
        if path:
            self.model.load_left_image_from_file(path)
            self.view.set_left_image(self.model.left_image)

    def load_right_image(self):
        path = self.view.prompt_for_image_path()
        if path:
            self.model.load_right_image_from_file(path)
            self.view.set_right_image(self.model.right_image)

    def load_left_image_from_camera(self):
        self.model.capture_left_image_from_camera()
        self.view.set_left_image(self.model.left_image)

    def load_right_image_from_camera(self):
        self.model.capture_right_image_from_camera()
        self.view.set_right_image(self.model.right_image)

    def copy_buf(self, src: str, dst: str):
        self.model.copy_buf(src, dst)
        match dst:
            case self.model.BUFFER1:
                self.view.set_buffer1_image(self.model.buffer1)
            case self.model.BUFFER2:
                self.view.set_buffer2_image(self.model.buffer2)
            case self.model.BUFFER3:
                self.view.set_buffer3_image(self.model.buffer3)
            case self.model.LEFT:
                self.view.set_left_image(self.model.left_image)
            case self.model.RIGHT:
                self.view.set_right_image(self.model.right_image)

    def transform(self):
        operation = self.view.get_operation()
        self.model.transform(operation)
        self.view.set_buffer3_image(self.model.buffer3)


    def low_pass(self):
        mat = self.model.low_pass_matrix()
        self.view.show_matrix(mat)

    def high_pass(self):
        mat = self.model.high_pass_matrix()
        self.view.show_matrix(mat)

    def filter(self):
        mat = self.view.get_matrix()
        self.model.filter_buffer2(mat)
        self.view.set_buffer3_image(self.model.buffer3)

    def threshold(self):
        #hreshold_value = self.view.get_threshold_value()
        threshold_value = 128
        self.model.threshold_buffer2(threshold_value)
        self.view.set_buffer3_image(self.model.buffer3)

    def dilate(self):
        self.model.dilate_buffer2()
        self.view.set_buffer3_image(self.model.buffer3)

    def erode(self):
        self.model.erode_buffer2()
        self.view.set_buffer3_image(self.model.buffer3)


