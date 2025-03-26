# Microplate-Viewer
Python script that creates a Tkinter-based graphical user interface for capturing images of microplate wells using Raspberry Pi.

It supports 96-well and 24-well plates, allowing users to click on a well and log their selections with a chosen magnification level. The interface includes:

- **User Input Fields:** For entering the user name, microplate ID, and selecting magnification.
- **Microplate Image Display:** Loads and displays an image of the selected microplate type.
- **Well Selection:** Clicking on a well identifies it and records it in a history log.
- **Image Capture (Raspberry Pi):** If running on a Raspberry Pi, it captures and saves images using libcamera-still.
- **History Logging:** Tracks selected wells and saved images.
The program starts from a main menu and opens a secondary window to view and interact with the microplate.
