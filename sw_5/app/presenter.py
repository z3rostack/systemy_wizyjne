class Presenter:
    """Presenter connects the view and the model."""

    def __init__(self, model, view):
        self.model = model
        self.view = view

        if self.view.button is None or self.view.label is None:
            raise RuntimeError("View does not expose required widgets (button/label)")

        self.view.button.clicked.connect(self.on_button_clicked)
        self.update_label(0)

    def on_button_clicked(self):
        count = self.model.increment()
        self.update_label(count)

    def update_label(self, count: int):
        if count == 0:
            self.view.label.setText("Hello — press the button")
        else:
            self.view.label.setText(f"Clicked {count} times")
