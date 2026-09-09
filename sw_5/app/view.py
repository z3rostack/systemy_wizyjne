import numpy as np
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QPushButton, QMessageBox, QSpinBox, QTextEdit
from PySide6.QtGui import QImage, QPixmap, QMouseEvent

class ClickableLabel(QLabel):
    clicked = Signal((int, int))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit(event.position().toPoint().x(),
                          event.position().toPoint().y())
        super().mousePressEvent(event)

class View:
    """Loads the UI and exposes the widgets used by the presenter."""
    _view = None

    @property
    def view(self):
        return self._view

    def __init__(self, ui_path: str):
        loader = QUiLoader()
        loader.registerCustomWidget(ClickableLabel)
        ui_file = QFile(ui_path)
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_path}")
        self._view = loader.load(ui_file)
        ui_file.close()
        if self._view is None:
            raise RuntimeError(f"Failed to load UI from: {ui_path}")

        # find widgets by objectName
        self.open_file_button = self._view.findChild(QPushButton, "open_file_button")
        self.clear_button = self._view.findChild(QPushButton, "clear_button")
        self.burn_step_button = self._view.findChild(QPushButton, "burn_step_button")
        self.burn_selected_button = self._view.findChild(QPushButton, "burn_selected_button")
        self.burn_all_button = self._view.findChild(QPushButton, "burn_all_button")
        self.show_object_button = self._view.findChild(QPushButton, "show_object_button")
        self.analyse_mech_button = self._view.findChild(QPushButton, "analyse_mech_button")
        self.object_spinbox = self._view.findChild(QSpinBox, "object_spinbox")
        self.object_label = self._view.findChild(QLabel, "object_label")
        self.mechanic_label = self._view.findChild(QLabel, "mechanic_label")
        self.image_label = self._view.findChild(ClickableLabel, "image_label")
        self.x_pos_label = self._view.findChild(QLabel, "x_pos_label")
        self.y_pos_label = self._view.findChild(QLabel, "y_pos_label")
        self.r_val_label = self._view.findChild(QLabel, "r_val_label")
        self.g_val_label = self._view.findChild(QLabel, "g_val_label")
        self.b_val_label = self._view.findChild(QLabel, "b_val_label")
        self.smoldering_label = self._view.findChild(QLabel, "smoldering_label")
        self.burning_label = self._view.findChild(QLabel, "burning_label")
        self.scorched_label = self._view.findChild(QLabel, "scorched_label")
        self.burnt_label = self._view.findChild(QLabel, "burnt_label")
        self.objects_found_label = self._view.findChild(QLabel, "objects_found_label")
        self.analyse_logs_text = self._view.findChild(QTextEdit, "analyse_log")

    def show(self):
        self._view.show()

    def _to_pixmap(self, image: np.ndarray) -> QPixmap:
        rgb_image = np.ascontiguousarray(image[:, :, ::-1])
        qt_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0],
                          rgb_image.strides[0], QImage.Format.Format_RGB888).copy()
        return QPixmap.fromImage(qt_image)

    def set_image(self, image: np.ndarray) -> None:
        self.image_label.setPixmap(self._to_pixmap(image))

    def set_object_image(self, image: np.ndarray) -> None:
        self.object_label.setPixmap(self._to_pixmap(image))

    def set_mechanic_image(self, image: np.ndarray) -> None:
        self.mechanic_label.setPixmap(self._to_pixmap(image))

    def set_object_range(self, count: int) -> None:
        self.object_spinbox.setMinimum(1 if count else 0)
        self.object_spinbox.setMaximum(max(count, 1))

    def get_object_number(self) -> int:
        return self.object_spinbox.value()

    def prompt_for_image_path(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self._view, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        return path

    def set_pixel_values(self, x: int, y: int, red: int, green: int, blue: int) -> None:
        self.x_pos_label.setText(str(x))
        self.y_pos_label.setText(str(y))
        self.r_val_label.setText(str(red))
        self.g_val_label.setText(str(green))
        self.b_val_label.setText(str(blue))

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self._view, "Error", message)

    def show_burn_result(self, result: dict) -> None:
        self.smoldering_label.setText(f"Smoldering: {result.get('smoldering', 0)}")
        self.burning_label.setText(f"Burning: {result.get('burning', 0)}")
        self.scorched_label.setText(f"Scorched: {result.get('scorched', 0)}")
        self.burnt_label.setText(f"Burnt: {result.get('burnt', 0)}")
        self.objects_found_label.setText(f"Objects found: 0")

    def show_burn_all_result(self, result: dict) -> None:
        self.smoldering_label.setText(f"Smoldering: {result.get('smoldering', 0)}")
        self.burning_label.setText(f"Burning: {result.get('burning', 0)}")
        self.scorched_label.setText(f"Scorched: {result.get('scorched', 0)}")
        self.burnt_label.setText(f"Burnt: {result.get('burnt', 0)}")
        self.objects_found_label.setText(f"Objects found: {result.get('objects_found', 0)}")

    def clear_log(self) -> None:
        self.analyse_logs_text.clear()

    def process_events(self) -> None:
        """Repaint the window while a long burn is running."""
        QApplication.processEvents()

    def append_log(self, message: str) -> None:
        self.analyse_logs_text.append(message)
