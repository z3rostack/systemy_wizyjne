import sys
import os
from PySide6.QtWidgets import QApplication

from app.model import Model
from app.view import View
from app.presenter import Presenter


def main():
    app = QApplication(sys.argv)
    ui_path = os.path.join(os.path.dirname(__file__), "mainwindow.ui")
    view = View(ui_path)
    model = Model()
    presenter = Presenter(model, view)
    view.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
