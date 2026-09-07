class Presenter:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.view.open_file_button.clicked.connect(self.open_image)
        self.view.clear_button.clicked.connect(self.clear_image)
        self.view.burn_button.clicked.connect(self.burn_image)
        self.view.image_label.clicked.connect(self.inspect_pixel)
        self.view.set_image(self.model.image)

    def open_image(self) -> None:
        path = self.view.prompt_for_image_path()
        if not path:
            return
        try:
            self.model.load_image(path)
        except ValueError as error:
            self.view.show_error(str(error))
            return
        self.view.set_image(self.model.image)

    def clear_image(self) -> None:
        self.model.clear()
        self.view.set_image(self.model.image)

    def inspect_pixel(self, x: int, y: int) -> None:
        try:
            red, green, blue = self.model.pixel(x, y)
        except ValueError:
            return
        self.view.set_pixel_values(x, y, red, green, blue)

    def burn_image(self) -> None:
        x = int(self.view.x_pos_label.text())
        y = int(self.view.y_pos_label.text())
        self.model.ignite(x, y)
        self.model.burn_all()
        self.view.set_image(self.model.image)
        smoldering, burning, scorched, burnt = self.model.fire_counts()
        self.view.show_status(
            f"Smoldering: {smoldering} | Burning: {burning} | "
            f"Scorched: {scorched} | Burnt: {burnt}"
        )
