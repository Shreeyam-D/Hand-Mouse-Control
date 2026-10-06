# Hand Mouse Control

A computer vision-based virtual mouse that allows users to control the computer cursor using hand gestures through a webcam.

## Features

* Real-time hand tracking
* Webcam-based cursor control
* Gesture-based mouse interaction
* Left-click control
* Smooth cursor movement
* No physical mouse required

## Technologies Used

* Python
* OpenCV
* MediaPipe
* NumPy
* PyAutoGUI

## How It Works

The webcam captures the user's hand in real time.

MediaPipe detects and tracks the hand landmarks. The program uses the position and movement of specific fingers to control the computer cursor and perform mouse actions.

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Run the Project

Run the Python file:

```bash
python hand_mouse_control.py
```

Make sure your webcam is connected and available.

## Project Structure

```text
hand-mouse-control/
│
├── hand_mouse_control.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

* Windows
* Python 3.x
* Webcam
* Camera permissions
* Working display and mouse-control permissions

## Future Improvements

* Add right-click gestures
* Add scrolling gestures
* Add drag-and-drop gestures
* Add customizable gestures
* Improve cursor smoothing
* Add a graphical interface

## Author

Shreeyam Dahikar

B.Tech Artificial Intelligence and Machine Learning Student
