from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QPushButton, QLabel

class View:
    """Loads the UI using QUiLoader and exposes widgets used by the presenter."""

    def __init__(self, ui_path: str):
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_path}")
        self.window = loader.load(ui_file)
        ui_file.close()
        if self.window is None:
            raise RuntimeError(f"Failed to load UI from: {ui_path}")

        # find widgets by objectName
        self.button = self.window.findChild(QPushButton, "pushButton")
        self.label = self.window.findChild(QLabel, "label")
