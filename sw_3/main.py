#!/usr/bin/python3
import sys

from PySide6.QtWidgets import QApplication

from app.model import ImageModel
from app.presenter import MainWindowPresenter
from app.view import MainWindowView


def main() -> None:
    app = QApplication(sys.argv)

    view = MainWindowView()
    model = ImageModel()
    view.presenter = MainWindowPresenter(model, view)

    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
