class Model:
    """Simple model that holds a counter."""

    def __init__(self):
        self.counter = 0

    def increment(self) -> int:
        """Increment the counter and return the new value."""
        self.counter += 1
        return self.counter
