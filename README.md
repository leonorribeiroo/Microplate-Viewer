# Microplate-Viewer
Python script that creates a Tkinter-based graphical user interface for capturing images of microplate wells using Raspberry Pi.

It allows users to:
- Select a well by clicking on an image of the microplate.
- Log selected wells with timestamps and magnification levels.
- Capture and save images using the Raspberry Pi Camera (if running on a Raspberry Pi).
- Maintain a history of selected wells and saved files.

The program starts from a main menu and opens a secondary window to view and interact with the microplate.

## Features
- Supports **96-well** and **24-well** plates
- Graphical selection of wells with automatic detection
- Magnification selection (10x, 20x, 40x, 100x)
- **Raspberry Pi Camera integration** for image capture
- History log of selected wells and saved files

## Installation
1. Clone the Repository:
    ```bash
   git clone https://github.com/seu-usuario/microplate-selector.git
   cd microplate-selector

3. Install dependencies:
   ``` bash
   pip install -r requirements.txt

5. Run the Script:
   ```bash
   python main.py

## Dependencies
- Python 3.x
- OpenCV (cv2)
- Pillow (PIL)
- Tkinter (built-in with Python)
- NumPy
- Bisect (standard library)

## Usage
1. Enter the User Name and Microplate ID.
2. Select the Microplate Type and Magnification.
3. Click Start to open the well selection interface.
4. Click on a well to log its selection and (if on Raspberry Pi) capture an image.
5. Click Finish to exit the program.

## Notes
If running on Raspberry Pi, ensure libcamera-still is installed for image capture.

Images are saved in the user's Pictures directory under:
```bash
~/Pictures/{User}/{Microplate}.
