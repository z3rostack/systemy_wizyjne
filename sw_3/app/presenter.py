from __future__ import annotations

from app.model import ImageModel
from app.view import MainWindowView

from PySide6.QtCore import QObject, Signal, Slot

class MainWindowPresenter:
    """Coordinates the view and model."""

    def __init__(self, model: ImageModel, view: MainWindowView) -> None:
        self.model = model
        self.view = view

        self._bind_events()
        self._refresh_left_image()
        self._refresh_right_image()
        self._refresh_left_line_image()
        self._refresh_right_line_image()
        
        self._refresh_lut_preview()

    def _bind_events(self) -> None:
        self.view.left_draw_button.clicked.connect(self.draw_left_rectangles)
        self.view.left_open_image_button.clicked.connect(self.open_left_image)
        self.view.left_camera_button.clicked.connect(self.capture_left_image)
        self.view.left_clear_button.clicked.connect(self.clear_left_canvas)

        self.view.right_draw_button.clicked.connect(self.draw_right_rectangles)
        self.view.right_open_image_button.clicked.connect(
            self.open_right_image)
        self.view.right_camera_button.clicked.connect(self.capture_right_image)
        self.view.right_clear_button.clicked.connect(self.clear_right_canvas)

        self.view.to_right_button.clicked.connect(self.copy_to_right)
        self.view.to_left_button.clicked.connect(self.copy_to_left)
        self.view.to_mono_button.clicked.connect(self.grayscale_to_right)

        self.view.x_pos_edit.textChanged.connect(self.update_position)
        self.view.y_pos_edit.textChanged.connect(self.update_position)
        self.view.left_image_label.clicked.connect(
            self.update_position_from_click)

        self.view.left_draw_line_button.clicked.connect(self.draw_left_line)
        self.view.right_draw_line_button.clicked.connect(self.draw_right_line)

        self.view.transform_button.clicked.connect(self.transform_with_lut)
        self.view.p1_edit.textChanged.connect(self.transform_preview)
        self.view.identity_radiobutton.toggled.connect(self.transform_preview)
        self.view.negative_radiobutton.toggled.connect(self.transform_preview)
        self.view.brightness_radiobutton.toggled.connect(self.transform_preview)
        self.view.threshold_radiobutton.toggled.connect(self.transform_preview)
        self.view.threshold2_radiobutton.toggled.connect(self.transform_preview)
        self.view.contrast_radiobutton.toggled.connect(self.transform_preview)
        self.view.zoom_in_button.clicked.connect(self.zoom_in)
        self.view.zoom_out_button.clicked.connect(self.zoom_out)

    def _refresh_left_image(self) -> None:
        self.view.display_left_image(self.model.left_image)

    def _refresh_left_line_image(self) -> None:
        self.view.display_left_line_image(self.model.left_line_image)

    def _refresh_right_image(self) -> None:
        self.view.display_right_image(self.model.right_image)

    def _refresh_right_line_image(self) -> None:
        self.view.display_right_line_image(self.model.right_line_image)

    def _refresh_lut_preview(self ) -> None:
        self.view.display_lut_preview(self.model.create_lut_preview(self.model.lut))

    def draw_left_rectangles(self) -> None:
        self.model.draw_left_rectangles()
        self._refresh_left_image()

    def draw_right_rectangles(self) -> None:
        self.model.draw_right_rectangles()
        self._refresh_right_image()

    def open_left_image(self) -> None:
        file_path = self.view.prompt_for_image_path()
        if not file_path:
            return

        try:
            self.model.load_left_from_file(file_path)
        except ValueError as error:
            self.view.show_error(str(error))
            return

        self._refresh_left_image()

    def open_right_image(self) -> None:
        file_path = self.view.prompt_for_image_path()
        if not file_path:
            return
        try:
            self.model.load_right_from_file(file_path)
        except ValueError as error:
            self.view.show_error(str(error))
            return

        self._refresh_right_image()

    def capture_left_image(self) -> None:
        try:
            self.model.capture_left_from_camera()
        except RuntimeError as error:
            self.view.show_error(str(error))
            return

        self._refresh_left_image()

    def capture_right_image(self) -> None:
        try:
            self.model.capture_right_from_camera()
        except RuntimeError as error:
            self.view.show_error(str(error))
            return

        self._refresh_right_image()

    def clear_left_canvas(self) -> None:
        self.model.clear()
        self._refresh_left_image()

    def clear_right_canvas(self) -> None:
        self.model.clear_right()
        self._refresh_right_image()

    def copy_to_right(self) -> None:
        red = self.view.red_checkbox.isChecked()
        green = self.view.green_checkbox.isChecked()
        blue = self.view.blue_checkbox.isChecked()
        self.model.copy_to_right(red, green, blue)
        self._refresh_right_image()

    def copy_to_left(self) -> None:
        red = self.view.red_checkbox.isChecked()
        green = self.view.green_checkbox.isChecked()
        blue = self.view.blue_checkbox.isChecked()
        self.model.copy_to_left(red, green, blue)
        self._refresh_left_image()

    def grayscale_to_right(self) -> None:
        self.model.grayscale_to_right()
        self._refresh_right_image()

    def update_position(self) -> None:
        try:
            x = int(self.view.x_pos_edit.text())
            y = int(self.view.y_pos_edit.text())
            r, g, b = self.model.get_rgb_values(x, y)
        except ValueError:
            return  # Ignore invalid input

        self.view.set_rgb_values(r, g, b)

    def update_position_from_click(self, x: int, y: int) -> None:
        self.view.x_pos_edit.setText(str(x))
        self.view.y_pos_edit.setText(str(y))

        r, g, b = self.model.get_rgb_values(x, y)
        self.view.set_rgb_values(r, g, b)

    def draw_left_line(self) -> None:
        self.model.draw_left_line(int(self.view.y_pos_edit.text()))
        self._refresh_left_line_image()

    def draw_right_line(self) -> None:
        self.model.draw_right_line(int(self.view.y_pos_edit.text()))
        self._refresh_right_line_image()

    @Slot(bool)
    def transform_preview(self, checked: bool) -> None:
        if not checked:
            return

        if self.view.identity_radiobutton.isChecked():
            self.model.create_identity_lut()
            self._refresh_lut_preview()
        elif self.view.negative_radiobutton.isChecked():
            self.model.create_negative_lut()
            self._refresh_lut_preview()
        elif self.view.brightness_radiobutton.isChecked():
            brightness = int(self.view.p1_edit.text())
            print(f"Brightness: {brightness}")
            self.model.create_brightness_lut(brightness)
            self._refresh_lut_preview()
        elif self.view.threshold_radiobutton.isChecked():
            threshold = int(self.view.p1_edit.text())
            print(f"Threshold: {threshold}")
            self.model.create_threshold_lut(threshold)
            self._refresh_lut_preview()
        elif self.view.threshold2_radiobutton.isChecked():
            thresholdA = int(self.view.p1_edit.text())
            thresholdB = int(self.view.p2_edit.text())
            print(f"Thresholds: {thresholdA}, {thresholdB}")
            self.model.create_threshold2_lut(thresholdA, thresholdB)
            self._refresh_lut_preview()
        elif self.view.contrast_radiobutton.isChecked():
            k = int(self.view.p1_edit.text())
            print(f"Contrast k: {k}")
            self.model.create_contrast_lut(k)
            self._refresh_lut_preview()

    def transform_with_lut(self) -> None:
        self.model.transform_with_lut()
        self._refresh_right_image()

    def _read_quarter(self) -> int:
        try:
            quarter = int(self.view.quater_edit.text())
        except ValueError as error:
            raise ValueError("Quarter must be a number from 1 to 4.") from error

        if quarter not in (1, 2, 3, 4):
            raise ValueError("Quarter must be one of: 1, 2, 3, 4.")

        return quarter

    def zoom_in(self) -> None:
        try:
            quarter = self._read_quarter()
            self.model.zoom_in(quarter)
        except ValueError as error:
            self.view.show_error(str(error))
            return

        self._refresh_right_image()

    def zoom_out(self) -> None:
        try:
            quarter = self._read_quarter()
            self.model.zoom_out(quarter)
        except ValueError as error:
            self.view.show_error(str(error))
            return

        self._refresh_right_image()