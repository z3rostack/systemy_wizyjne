from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindowView(QMainWindow):
    """Qt view responsible for rendering widgets and dialogs."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("OpenCV Task 1")

        central_widget = QWidget()

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_upper_buttons_layout = QHBoxLayout()
        left_boton_buttons_layout = QHBoxLayout()

        self.draw_button = QPushButton("Draw rectangles")
        self.open_image_button = QPushButton("Open image")
        self.camera_button = QPushButton("Get image from camera")
        self.clear_button = QPushButton("Clear")
        self.image_label = QLabel()

        self.right_image_label = QLabel()
        
        # Properities
        self.image_label.setMinimumSize(320, 240)
        self.right_image_label.setMinimumSize(320, 240)

        # Set layouts
        left_upper_buttons_layout.addWidget(self.draw_button)
        left_upper_buttons_layout.addWidget(self.open_image_button)
        left_upper_buttons_layout.addWidget(self.camera_button)

        left_boton_buttons_layout.addWidget(self.clear_button)

        left_layout.addLayout(left_upper_buttons_layout)
        left_layout.addWidget(self.image_label)
        left_layout.addLayout(left_boton_buttons_layout)

        main_layout.addLayout(left_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

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

    def display_image(self, image: np.ndarray) -> None:
        self.image_label.setPixmap(self._mat_to_pixmap(image))

    def prompt_for_image_path(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(self)
        return file_path

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)
