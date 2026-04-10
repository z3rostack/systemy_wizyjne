# Computer Vision Course 1

A small desktop application that combines OpenCV image processing with a PyQt6 user interface.

The app lets you:

- open an image from disk,
- capture a frame from your default camera,
- draw sample rectangles on the current image,
- clear the canvas and start again.

This project is a lightweight starter for experimenting with OpenCV in a desktop GUI.

The codebase follows the MVP (Model-View-Presenter) pattern to keep UI rendering, application flow, and image-processing logic separate.

## Tech Stack

- Python
- PySide6
- OpenCV (`opencv-python`)
- NumPy
- `uv` for dependency management and running the app

## Requirements

- Python `3.14+`
- A working webcam if you want to use camera capture
- Optional UV

## Running the App

Start the application with:

Using UV:
```bash
uv run main.py
```