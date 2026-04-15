#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication

from app.view import MainWindowView
from app.model import Model
from app.presenter import MainWindowPresenter

def main():
    app = QApplication(sys.argv)

    model = Model()
    view = MainWindowView()
    presenter = MainWindowPresenter(view, model)
    
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
