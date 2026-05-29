import cv2
import numpy as np

from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
)

UI_FILE = "mainwindow.ui"

class MainWindowView:
    _view = None

    @property
    def view(self):
        return self._view
    
    def __init__(self):
        self.loader = QUiLoader()
        self._view = self.loader.load(UI_FILE, None)

    def _mat_to_pixmap(self, image: np.ndarray) -> QPixmap:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        bytes_per_line = channels * width

        qt_image = QImage(
            rgb_image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )

        return QPixmap.fromImage(qt_image)

    def show(self):
        self._view.show()

    def prompt_for_image_path(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(self._view, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        return file_path

    def set_left_image(self, image: np.ndarray):
        pixmap = self._mat_to_pixmap(image)
        self._view.left_label.setPixmap(pixmap)

    def set_right_image(self, image: np.ndarray):
        pixmap = self._mat_to_pixmap(image)
        self._view.right_label.setPixmap(pixmap)

    def set_buffer1_image(self, image: np.ndarray):
        pixmap = self._mat_to_pixmap(image)
        self._view.buf1_label.setPixmap(pixmap)

    def set_buffer2_image(self, image: np.ndarray):
        pixmap = self._mat_to_pixmap(image)
        self._view.buf2_label.setPixmap(pixmap) 

    def set_buffer3_image(self, image: np.ndarray):
        pixmap = self._mat_to_pixmap(image)
        self._view.buf3_label.setPixmap(pixmap)

    def get_operation(self) -> str:
        if self.view.and_radio.isChecked():
            return "AND"
        elif self.view.or_radio.isChecked():
            return "OR"
        elif self.view.xor_radio.isChecked():
            return "XOR"
        else:
            raise ValueError("No operation selected")

    def show_matrix(self, matrix: np.ndarray):
        self.view.w1.setValue(matrix[0, 0])
        self.view.w2.setValue(matrix[0, 1])
        self.view.w3.setValue(matrix[0, 2])
        self.view.w4.setValue(matrix[1, 0])
        self.view.w5.setValue(matrix[1, 1])
        self.view.w6.setValue(matrix[1, 2])
        self.view.w7.setValue(matrix[2, 0])
        self.view.w8.setValue(matrix[2, 1])
        self.view.w9.setValue(matrix[2, 2])

    def get_matrix(self) -> np.ndarray:
        w1 = int(self.view.w1.text())
        w2 = int(self.view.w2.text())
        w3 = int(self.view.w3.text())
        w4 = int(self.view.w4.text())
        w5 = int(self.view.w5.text())
        w6 = int(self.view.w6.text())
        w7 = int(self.view.w7.text())
        w8 = int(self.view.w8.text())
        w9 = int(self.view.w9.text())

        return np.array([[w1, w2, w3],
                         [w4, w5, w6],
                         [w7, w8, w9]])
    
    def get_add(self):
        return self.view.add_checkbox.isChecked()
    
    def get_mono(self):
        return self.view.mono_checkbox.isChecked()
    
    def get_threshold_value(self) -> int:
        return int(self.view.threshold_spinbox.value())
    
    def get_thresholds_value(self) -> int:
        red_lower = int(self.view.red_lthreshold.value())
        red_upper = int(self.view.red_uthreshold.value())
        green_lower = int(self.view.green_lthreshold.value())
        green_upper = int(self.view.green_uthreshold.value())
        blue_lower = int(self.view.blue_lthreshold.value())
        blue_upper = int(self.view.blue_uthreshold.value())
        return (red_lower, red_upper, green_lower, green_upper, blue_lower, blue_upper)