import numpy as np
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Signal
from PySide6.QtWidgets import QFileDialog, QLabel, QPushButton, QMessageBox
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
        self.burn_button = self._view.findChild(QPushButton, "burn_button")
        self.image_label = self._view.findChild(ClickableLabel, "image_label")
        self.x_pos_label = self._view.findChild(QLabel, "x_pos_label")
        self.y_pos_label = self._view.findChild(QLabel, "y_pos_label")
        self.r_val_label = self._view.findChild(QLabel, "r_val_label")
        self.g_val_label = self._view.findChild(QLabel, "g_val_label")
        self.b_val_label = self._view.findChild(QLabel, "b_val_label")

    def show(self):
        self._view.show()

    def set_image(self, image: np.ndarray) -> None:
        rgb_image = np.ascontiguousarray(image[:, :, ::-1])
        qt_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0],
                          rgb_image.strides[0], QImage.Format.Format_RGB888).copy()
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

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

    def show_status(self, message: str) -> None:
        self._view.statusBar().showMessage(message)
