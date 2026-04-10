from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QIntValidator, QMouseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QLineEdit,
    QRadioButton,
    QSizePolicy,
)

from app.constants import IMAGE_HEIGHT, IMAGE_WIDTH, LINE_IMAGE_HEIGHT


class ClickableLabel(QLabel):
    clicked = Signal((int, int))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit(event.position().toPoint().x(),
                          event.position().toPoint().y())
        super().mousePressEvent(event)


class MainWindowView(QMainWindow):
    """Qt view responsible for rendering widgets and dialogs."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("OpenCV Task 3")

        central_widget = QWidget()

        # Layouts
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_upper_buttons_layout_a = QHBoxLayout()
        left_upper_buttons_layout_b = QHBoxLayout()
        left_upper_buttons_layout_ab = QVBoxLayout()
        left_bottom_buttons_layout = QHBoxLayout()

        transform_buttons_layout = QVBoxLayout()

        right_layout = QVBoxLayout()
        right_upper_buttons_layout_a = QHBoxLayout()
        right_upper_buttons_layout_b = QHBoxLayout()
        right_upper_buttons_layout_ab = QVBoxLayout()
        right_bottom_buttons_layout = QHBoxLayout()

        operations_layout = QVBoxLayout()
        transformations_layout = QVBoxLayout()
        preview_layout = QHBoxLayout()
        parameters_layout = QHBoxLayout()
        selector_layout = QVBoxLayout()
        details_layout = QVBoxLayout()
        zoom_layout = QVBoxLayout()

        # Widgets

        self.left_draw_button = QPushButton("Draw rectangles")
        self.left_open_image_button = QPushButton("Open image")
        self.left_camera_button = QPushButton("Camera")
        self.left_clear_button = QPushButton("Clear")
        self.left_draw_line_button = QPushButton("Draw line")
        self.left_image_label = ClickableLabel()
        self.left_line_image_label = QLabel()

        self.x_pos_label = QLabel("X:")
        self.x_pos_edit = QLineEdit("0")
        self.y_pos_label = QLabel("Y:")
        self.y_pos_edit = QLineEdit("0")
        self.red_val_label = QLabel("R:")
        self.green_val_label = QLabel("G:")
        self.blue_val_label = QLabel("B:")

        self.empty = QLabel("")

        self.to_right_button = QPushButton(">>")
        self.to_left_button = QPushButton("<<")
        self.to_mono_button = QPushButton("Mono>>")
        self.red_checkbox = QCheckBox(text="Red")
        self.green_checkbox = QCheckBox(text="Green")
        self.blue_checkbox = QCheckBox(text="Blue")

        self.right_draw_button = QPushButton("Draw rectangles")
        self.right_open_image_button = QPushButton("Open image")
        self.right_camera_button = QPushButton("Camera")
        self.right_clear_button = QPushButton("Clear")
        self.right_draw_line_button = QPushButton("Draw line")
        self.right_image_label = QLabel()
        self.right_line_image_label = QLabel()

        self.lut_preview_label = QLabel()
        self.transform_button = QPushButton("Transform")
        self.r_transform_checkbox = QCheckBox(text="R")
        self.g_transform_checkbox = QCheckBox(text="G")
        self.b_transform_checkbox = QCheckBox(text="B")
        self.identity_radiobutton = QRadioButton("Identity")
        self.negative_radiobutton = QRadioButton("Negative")
        self.brightness_radiobutton = QRadioButton("Brightness")
        self.threshold_radiobutton = QRadioButton("Threshold")
        self.threshold2_radiobutton = QRadioButton("Threshold2")
        self.contrast_radiobutton = QRadioButton("Contrast")
        self.p1_edit = QLineEdit("128")
        self.p2_edit = QLineEdit("0")

        self.quater_edit = QLineEdit("0")
        self.zoom_in_button = QPushButton("Zoom in")
        self.zoom_out_button = QPushButton("Zoom out")  

        # Properities
        self.left_image_label.setMinimumSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.right_image_label.setMinimumSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.left_line_image_label.setMinimumSize(IMAGE_WIDTH, LINE_IMAGE_HEIGHT)
        self.right_line_image_label.setMinimumSize(IMAGE_WIDTH, LINE_IMAGE_HEIGHT)
        self.lut_preview_label.setMinimumSize(64, 64)
        self.lut_preview_label.setMaximumSize(64, 64)

        only_int = QIntValidator()
        only_int.setRange(0, 255)
        self.x_pos_edit.setValidator(only_int)
        self.x_pos_edit.setFixedWidth(50)
        self.y_pos_edit.setValidator(only_int)
        self.y_pos_edit.setFixedWidth(50)
        self.p1_edit.setValidator(only_int)
        self.p2_edit.setValidator(only_int)
        quarter_int = QIntValidator()
        quarter_int.setRange(1, 4)
        self.quater_edit.setValidator(quarter_int)
        self.quater_edit.setFixedWidth(50)
        self.identity_radiobutton.setChecked(True)
        self.r_transform_checkbox.setChecked(True)
        self.g_transform_checkbox.setChecked(True)
        self.b_transform_checkbox.setChecked(True)

        # Set layouts

        ## Left side
        left_upper_buttons_layout_a.addWidget(self.left_draw_button)
        left_upper_buttons_layout_a.addWidget(self.left_open_image_button)
        left_upper_buttons_layout_a.addWidget(self.left_camera_button)

        left_upper_buttons_layout_b.addWidget(self.x_pos_label)
        left_upper_buttons_layout_b.addWidget(self.x_pos_edit)
        left_upper_buttons_layout_b.addWidget(self.y_pos_label)
        left_upper_buttons_layout_b.addWidget(self.y_pos_edit)
        left_upper_buttons_layout_b.addWidget(self.red_val_label)
        left_upper_buttons_layout_b.addWidget(self.green_val_label)
        left_upper_buttons_layout_b.addWidget(self.blue_val_label)

        left_upper_buttons_layout_ab.addLayout(left_upper_buttons_layout_a)
        left_upper_buttons_layout_ab.addLayout(left_upper_buttons_layout_b)

        left_bottom_buttons_layout.addWidget(self.left_clear_button)
        left_bottom_buttons_layout.addWidget(self.left_draw_line_button)

        left_layout.addLayout(left_upper_buttons_layout_ab)
        left_layout.addWidget(self.left_image_label)
        left_layout.addLayout(left_bottom_buttons_layout)
        left_layout.addWidget(self.left_line_image_label)

        ## Middle
        transform_buttons_layout.addWidget(self.to_right_button)
        transform_buttons_layout.addWidget(self.red_checkbox)
        transform_buttons_layout.addWidget(self.green_checkbox)
        transform_buttons_layout.addWidget(self.blue_checkbox)
        transform_buttons_layout.addWidget(self.to_left_button)
        transform_buttons_layout.addWidget(self.to_mono_button)

        ## Right side
        right_upper_buttons_layout_a.addWidget(self.right_draw_button)
        right_upper_buttons_layout_a.addWidget(self.right_open_image_button)
        right_upper_buttons_layout_a.addWidget(self.right_camera_button)

        right_upper_buttons_layout_b.addWidget(self.empty)

        right_upper_buttons_layout_ab.addLayout(right_upper_buttons_layout_a)
        right_upper_buttons_layout_ab.addLayout(right_upper_buttons_layout_b)

        right_bottom_buttons_layout.addWidget(self.right_clear_button)
        right_bottom_buttons_layout.addWidget(self.right_draw_line_button)

        right_layout.addLayout(right_upper_buttons_layout_ab)
        right_layout.addWidget(self.right_image_label)
        right_layout.addLayout(right_bottom_buttons_layout)
        right_layout.addWidget(self.right_line_image_label)

        preview_layout.addWidget(self.lut_preview_label)
        preview_layout.addWidget(self.transform_button)

        selector_layout.addWidget(self.identity_radiobutton)
        selector_layout.addWidget(self.negative_radiobutton)
        selector_layout.addWidget(self.brightness_radiobutton)
        selector_layout.addWidget(self.threshold_radiobutton)
        selector_layout.addWidget(self.threshold2_radiobutton)
        selector_layout.addWidget(self.contrast_radiobutton)

        details_layout.addWidget(self.r_transform_checkbox)
        details_layout.addWidget(self.g_transform_checkbox)
        details_layout.addWidget(self.b_transform_checkbox)
        details_layout.addWidget(self.p1_edit)
        details_layout.addWidget(self.p2_edit)

        parameters_layout.addLayout(selector_layout)
        parameters_layout.addLayout(details_layout)

        transformations_layout.addLayout(preview_layout)
        transformations_layout.addLayout(parameters_layout)

        zoom_layout.addWidget(self.quater_edit)
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button) 

        ## Operations
        operations_layout.addLayout(transformations_layout)
        operations_layout.addLayout(zoom_layout)

        ## Main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(transform_buttons_layout)
        main_layout.addLayout(right_layout)
        main_layout.addLayout(operations_layout)

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

    def display_left_image(self, image: np.ndarray) -> None:
        self.left_image_label.setPixmap(self._mat_to_pixmap(image))

    def display_left_line_image(self, image: np.ndarray) -> None:
        self.left_line_image_label.setPixmap(self._mat_to_pixmap(image))

    def display_right_image(self, image: np.ndarray) -> None:
        self.right_image_label.setPixmap(self._mat_to_pixmap(image))

    def display_right_line_image(self, image: np.ndarray) -> None:
        self.right_line_image_label.setPixmap(self._mat_to_pixmap(image))

    def display_lut_preview(self, image: np.ndarray) -> None:
        self.lut_preview_label.setPixmap(self._mat_to_pixmap(image))    

    def prompt_for_image_path(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        return file_path

    def set_rgb_values(self, red: int, green: int, blue: int) -> None:
        self.red_val_label.setText(f"R: {red}")
        self.green_val_label.setText(f"G: {green}")
        self.blue_val_label.setText(f"B: {blue}")

    def display_lut_preview(self, image: np.ndarray) -> None:
        self.lut_preview_label.setPixmap(self._mat_to_pixmap(image))

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)
