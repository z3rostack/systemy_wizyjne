from __future__ import annotations

from app.model import ImageModel
from app.view import MainWindowView


class MainWindowPresenter:
    """Coordinates the view and model."""

    def __init__(self, model: ImageModel, view: MainWindowView) -> None:
        self.model = model
        self.view = view

        self._bind_events()
        self._refresh_image()

    def _bind_events(self) -> None:
        self.view.draw_button.clicked.connect(self.draw_rectangles)
        self.view.open_image_button.clicked.connect(self.open_image)
        self.view.camera_button.clicked.connect(self.capture_image)
        self.view.clear_button.clicked.connect(self.clear_canvas)
    
    def _refresh_image(self) -> None:
        self.view.display_image(self.model.image)

    def draw_rectangles(self) -> None:
        self.model.draw_rectangles()
        self._refresh_image()

    def open_image(self) -> None:
        file_path = self.view.prompt_for_image_path()
        if not file_path:
            return

        try:
            self.model.load_from_file(file_path)
        except ValueError as error:
            self.view.show_error(str(error))
            return

        self._refresh_image()

    def capture_image(self) -> None:
        try:
            self.model.capture_from_camera()
        except RuntimeError as error:
            self.view.show_error(str(error))
            return

        self._refresh_image()

    def clear_canvas(self) -> None:
        self.model.clear()
        self._refresh_image()
