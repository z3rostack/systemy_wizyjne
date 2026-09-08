class Presenter:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.view.open_file_button.clicked.connect(self.open_image)
        self.view.clear_button.clicked.connect(self.clear_image)
        self.view.burn_selected_button.clicked.connect(self.burn_selected)
        self.view.burn_all_button.clicked.connect(self.burn_all_objects)
        self.view.show_object_button.clicked.connect(self.show_object)
        self.view.image_label.clicked.connect(self.inspect_pixel)
        self.view.analyse_mech_button.clicked.connect(self.analyse_mechanic)

        self.view.set_image(self.model.image)
        self.view.set_object_image(self.model.objects_image)
        self.view.set_mechanic_image(self.model.mechanic_image)

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
        self.view.set_object_image(self.model.objects_image)
        self.view.set_mechanic_image(self.model.mechanic_image)

    def inspect_pixel(self, x: int, y: int) -> None:
        try:
            red, green, blue = self.model.pixel(x, y)
        except ValueError:
            return
        self.view.set_pixel_values(x, y, red, green, blue)

    def burn_selected(self) -> None:
        x = int(self.view.x_pos_label.text())
        y = int(self.view.y_pos_label.text())
        self.model.ignite(x, y)
        self.model.burn_cycle()
        self.view.set_image(self.model.image)
        smoldering, burning, scorched, burnt = self.model.fire_counts()
        self.view.show_status(
            f"Smoldering: {smoldering} | Burning: {burning} | "
            f"Scorched: {scorched} | Burnt: {burnt}"
        )

    def burn_all_objects(self) -> None:
        self.model.burn_all()
        self.view.set_image(self.model.image)
        self.view.set_object_image(self.model.objects_image)
        self.view.set_object_range(self.model.object_count)
        self.view.show_status(f"Objects: {self.model.object_count}")

    def show_object(self) -> None:
        try:
            image = self.model.object_image(self.view.get_object_number())
        except ValueError as error:
            self.view.show_error(str(error))
            return
        self.view.set_object_image(image)

    def analyse_mechanic(self) -> None:
        try:
            image = self.model.mechanic_analysis()
        except ValueError as error:
            self.view.show_error(str(error))
            return
        self.view.set_mechanic_image(image)
        self.view.clear_log()
        for name, value in self.model.mechanic_data.items():
            self.view.append_log(f"{name}: {value:.2f}")
