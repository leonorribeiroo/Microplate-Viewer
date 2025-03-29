# Well Viewer
Python script developed in collaboration with i3S (Porto, Portugal; [www.i3s.up.pt](www.i3s.up.pt)) that creates a Tkinter-based graphical user interface for capturing and automatically anotating images of microplate wells using a *Raspberry Pi 4B SBC* and a *Raspberry Pi High Quality (HQ) C(S)-mount camera* on a trinocular stereo microscope.


It allows users to:
- Record the image of a microplate well (with well position, timestamp and magnification) by clicking on the corresponding position on a schematic representation of the microplate.
- Log selected wells with timestamps and magnification levels.
- Maintain a history of selected wells and saved files.

The program starts from a main menu and opens a secondary window to view and interact with the microplate.

## Features
- Supports **96-well** and **24-well** plates
- Graphical selection of wells
- Selectable magnification level (10x, 20x, 30x, 40x, 50x, 63x for our Nikon SMZ800 with 10x eyepieces)
- **Raspberry Pi Camera integration** for image capture
- History log of selected wells and saved files

## Installation
1. Update the System
   Open a terminal on your Raspberry Pi and run:
    ```bash
   sudo apt update && sudo apt upgrade -y
   
2. Install Dependencies
3. The required libraries can be installed using apt. Run:
   ```bash
   sudo apt install -y python3-tk python3-opencv python3-pil

4. Clone the Repository
   If git is not installed, first install it with:
   ```bash
   sudo apt install -y git

   Then, clone this repository:
   ```bash
   git clone https://github.com/leonorribeiroo/WellView

   Change the directory:
   ```bash
   cd WellView
   
5. Run the Script:
   ```bash
   python3 wellview.py

## Dependencies
Pre-installed with Python:
- Tkinter 
- Bisect 
- datetime
- os
- subprocess

Requires installation on Rasberry Pi:
- OpenCV (cv2)
- Pillow (PIL)
- rpicam

## Usage
1. Enter the User Name and Microplate ID.
2. Select the Microplate Type
3. Select the Magnification (can be changed on the fly in the secondary interface).
4. Click Start to open the well selection interface.
5. Click on a well to log its selection and capture an image.
6. Click Back to return to the primary menu (and change the Microplate ID).
7. Click Finish to exit the program.


## Notes
Ensure that rpicam-still is installed for image capture.

Images are saved in the user's Pictures directory under:
```bash
~/Pictures/{User}/{Microplate}.
