# Systemy wizyjne

Computer vision lab apps written in Python with PySide6, NumPy and OpenCV.
Each project is a standalone desktop app following the MVP (Model-View-Presenter) pattern.

## Projects

| Project | Summary |
| --- | --- |
| `sw_1` | Basics: open an image, capture a camera frame, draw rectangles, clear the canvas. |
| `sw_2` | Two canvases: copy images left/right by RGB channel, grayscale conversion, pixel inspection, line drawing. |
| `sw_3` | Point operations via LUT: negative, brightness, threshold, contrast, plus zoom in/out. |
| `sw_4` | Buffers and neighbourhood operations: low/high pass, Sobel, Prewitt, Gauss, Laplace, custom kernels, dilate/erode, open/close, colour thresholding. |
| `sw_5` | Segmentation by a "fire" (region growing) algorithm, per-object preview and mechanics analysis (area, centroid, moments, principal axes). |
| `proj` | Placeholder for the final project. |

## Tooling

All projects use [uv](https://docs.astral.sh/uv/) for dependency management and running.
Dependencies and the required Python version (`3.14+`) are declared in each `pyproject.toml`,
so there is no need to create a virtual environment or install packages by hand.

## Running

Enter a project directory and run it — uv sets up the environment on first run:

```bash
cd sw_5
uv run main.py
```
