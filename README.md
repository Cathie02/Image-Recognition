# Window Capture and Image Recognition

This project provides a Python-based solution for capturing frames from a specified window on the screen and performing image recognition tasks within those frames. It is particularly useful for automating tasks that involve identifying specific elements or patterns within a game or application window.

## Features

- **Window Capture:** The `WindowCapture` class allows you to capture frames from a specified window on the screen. It utilizes the `win32gui` library to interact with the Windows API and obtain screen captures.

- **Image Recognition:** The `Vision` class performs image recognition tasks by matching a template image (needle) within a larger image (haystack). It uses OpenCV to find instances of the template image within the larger image and returns their coordinates.

- **Rectangle Drawer:** The `RectangleDrawer` class is a threaded component used to draw rectangles around the detected instances of the template image in the captured frames. It runs in parallel with other tasks to improve performance.

- **Main Script:** The `main.py` script coordinates the entire process. It captures frames using `WindowCapture`, performs image recognition using `Vision`, and draws rectangles using `RectangleDrawer`. Additionally, it handles user input, such as stopping the script using the escape key.

## Usage

1. Install the required dependencies by running `pip install -r requirements.txt`.

2. Configure the `main.py` script by specifying the window name and the path to the template image (needle).

3. Run the `main.py` script to start capturing frames and performing image recognition tasks. Use the escape key to stop the script.

## Dependencies

- Python 3.x
- OpenCV (`opencv-python`)
- `win32gui` (Windows-specific)
- `numpy`

## Example

Here's a simple example of how to use this project:

```python
python main.py
```

This will start capturing frames from the specified window and perform image recognition tasks within those frames.

## License
This project is licensed under the GPL-3.0 License - see the [LICENSE](https://raw.githubusercontent.com/Cathie02/Image-Recognition/main/LICENSE.md) file for details.
