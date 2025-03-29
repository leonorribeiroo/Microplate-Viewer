from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, W, E, Toplevel, Canvas, Text, Frame
import cv2
from bisect import bisect
from datetime import datetime
import os
from PIL import Image, ImageTk
import subprocess

saved_files = []

# Plate dimensions
pxRo_dict = {
    '96-well plate': [0, 63.3, 117.3, 136.8, 190.8, 206.8, 260.8, 278.85, 332.85, 350.9,
               404.9, 422.95, 476.95, 495, 549, 567.05, 621.05],
    '24-well plate': [0, 108.94, 220.94, 254.29, 366.29, 399.64, 511.64, 545.64, 657.64]
}
pxCo_dict = {
    '96-well plate': [0, 88.3, 142.3, 160.35, 214.35, 232.4, 286.4, 304.45, 358.45, 376.5,
               430.5, 448.55, 502.55, 520.6, 574.6, 592.65, 646.65, 664.7, 718.7, 736.75,
               790.75, 808.8, 862.8, 880.85, 934.85],
    '24-well plate': [0, 123.27, 235.27, 267.77, 379.77, 412.27, 524.27, 556.77, 668.77, 701.27,
               813.27, 845.77, 957.77]
}

# Function to verify if the code is running on a Raspberry Pi
def is_raspberry_pi():
        """Verify if the code is running on a Raspberry Pi."""
        try:
            with open("/proc/device-tree/model", "r") as f:
                if "Raspberry Pi" in f.read():
                    return True
        except FileNotFoundError:
            return False
        return False

# Function to select the well
def sel_well(x, y, pltSel):
    pxCo = pxCo_dict[pltSel]
    iCo = bisect(pxCo, x)
    pxRo = pxRo_dict[pltSel]
    iRo = bisect(pxRo, y)
    
    if iCo > 0 and iRo > 0 and iCo % 2 == 0 and iRo % 2 == 0:
        strg = 'ABCDEFGH'
        selected = strg[int(iRo/2-1)] + str(int(iCo/2))
    else:
        selected = ''
    
    return selected

# Function to open the image window
def open_image_window():
    global img_cv, img_tk, img_pil, canvas, pltSel, userNm, plateNm, history_text, logo_tk
    userNm = name_label_field.get().strip() or "DefaultUser"
    plateNm = plate_label_field.get().strip() or "DefaultPlate"
    pltSel = plate_value.get() if plate_value.get() in pxCo_dict else "96-well plate"
    img_path = f"images/{pltSel.replace('-well plate', '')}-Well_plate.jpg"
    
    # Get the magnification value
    magnification = StringVar()
    magnification.set(magnification_value.get())  # Copy the value from the main window

    if not os.path.exists(img_path):
        print(f"Error: The image {img_path} does not exist.")
        return
    
    img_cv = cv2.imread(img_path)
    if img_cv is None:
        print("Error: The image could not be loaded.")
        return
    
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_cv)
    img_tk = ImageTk.PhotoImage(img_pil)
    
    image_window = Toplevel(main_window)
    image_window.title("Microplate Viewer")
    
    # Create a Frame for the text, at the top
    top_frame = Frame(image_window)
    top_frame.pack(fill="x")
    
    # Add the I3Slogo
    logo_image = Image.open("logo/logo2.png")
    logo_image = logo_image.resize((300, 145))  
    logo_tk = ImageTk.PhotoImage(logo_image)
    logo_label = Label(image_window, image=logo_tk)
    logo_label.place(relx=0.0, rely=0.0, anchor="nw", y=-25)

    # Add the text inside the top_frame 
    Label(top_frame, text="Select the well to capture", font=("Arial", 24, "bold")).pack()
    Label(top_frame, text=f"User: {userNm}", font=("Arial", 16)).pack()
    Label(top_frame, text=f"Microplate ID: {plateNm}", font=("Arial", 16)).pack()

    # Create a Frame for the image (with left and right padding frames)
    image_frame = Frame(image_window)
    image_frame.pack(fill="both", expand=True, padx=20, pady=20)  

    # Create the canvas to display the image in the center frame
    center_frame = Frame(image_frame)
    center_frame.grid(row=0, column=1)

    canvas = Canvas(center_frame, width=img_pil.width, height=img_pil.height)
    canvas.pack(fill="both", expand=True)

    # Display the image on the canvas
    canvas.create_image(0, 0, anchor="nw", image=img_tk)

    right_frame = Frame(image_frame, width=200)  # This will hold the buttons and history
    right_frame.grid(row=0, column=2, sticky="ns")

    # Create a frame to organize the buttons and history inside the right_frame
    history_frame = Frame(right_frame)
    history_frame.pack(pady=10, fill="x")

    # History Label 
    history_label = Label(history_frame, text="Selected Wells History:")
    history_label.grid(row=0, column=0, columnspan=3, pady=10)  

    # History Text Box 
    history_text = Text(history_frame, height=10, width=50, state='disabled')
    history_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    Button(history_frame, text="Back", command=image_window.destroy).grid(row=2, column=0, padx=10, pady=5, sticky="e")

    Label(history_frame, text="Magnification:").grid(row=2, column=1, padx=10)

    Button(history_frame, text="Finish", command=main_window.quit).grid(row=2, column=2, padx=10, pady=5, sticky="w")

    OptionMenu(history_frame, magnification, "10x", "20x", "30x", "40x", "50x", "63x").grid(row=3, column=1, padx=10, pady=5)

    # Function to handle the click event on a well
    def click_canvas(event):
        global img_cv, img_pil, img_tk
        x, y = event.x, event.y
        selected = sel_well(x, y, pltSel)
        
        if selected:
            current_magnification = magnification.get()

            # Update the history
            history_text.config(state='normal')
            history_text.insert('end', f"{datetime.now().strftime('%H:%M:%S')} - {current_magnification} - {selected}\n")
            history_text.config(state='disabled')

            # Copy the image to display the selected well (to keep the original image)
            img_display = img_cv.copy()
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(selected, font, 1, 2)[0]
            text_x = x - text_size[0] // 2
            text_y = y + text_size[1] // 2
            cv2.putText(img_display, selected, (text_x, text_y), font, 1, (255, 0, 0), 2)
            
            img_pil = Image.fromarray(img_display)
            img_tk = ImageTk.PhotoImage(img_pil)
            canvas.create_image(0, 0, anchor="nw", image=img_tk)

            # Save the image taken with the Raspberry Pi
            if is_raspberry_pi():
                current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                home_dir = os.path.expanduser("~")
                pictures_dir = os.path.join(home_dir, "Pictures")
                folderpath = os.path.join(pictures_dir, userNm, plateNm)
                os.makedirs(folderpath, exist_ok=True)

                file_name = os.path.join(folderpath, f"{current_datetime}_{selected}_{current_magnification}.png")
 
                try:
                    subprocess.run(["libcamera-still", "-e", "png", "-o", file_name], check=True)
                    print(f"Image captured and saved: {file_name}")
                    
                    # Update the history if the image was saved
                    history_text_main.config(state='normal')
                    history_text_main.insert('end', file_name + '\n')
                    history_text_main.config(state='disabled')

                except subprocess.CalledProcessError as e:
                    print(f"Error capturing image with Raspberry Pi: {e}")
    
    canvas.bind("<Button-1>", click_canvas)
    

def start_program():
    open_image_window()

# Main window setup
main_window = Tk()
main_window.title('Main Menu')
main_window.columnconfigure(0, weight=1)
main_window.columnconfigure(1, weight=1)

# Add the I3S logo 
logo_image = Image.open("logo/logo.png")
logo_image = logo_image.resize((50, 40))  
logo_tk = ImageTk.PhotoImage(logo_image)
logo_label = Label(main_window, image=logo_tk)
logo_label.image = logo_tk  
logo_label.place(relx=1.0, rely=1.0, anchor="se")

Label(main_window, text="User:").grid(column=0, row=1)
name_label_field = Entry()
name_label_field.grid(column=1, row=1)

Label(main_window, text="Microplate ID:").grid(column=0, row=2)
plate_label_field = Entry()
plate_label_field.grid(column=1, row=2)

Label(main_window, text="Magnification:").grid(column=0, row=3)
magnification_value = StringVar(main_window)
magnification_value.set("10x")  # Standard value
OptionMenu(main_window, magnification_value, "10x", "20x", "30x", "40x", "50x", "63x").grid(column=1, row=3)

Label(main_window, text="Microplate type").grid(column=0, row=4)
plate_list = ["96-well plate", "24-well plate"]
plate_value = StringVar(main_window)
plate_value.set("Select a microplate type")
OptionMenu(main_window, plate_value, *plate_list).grid(column=0, row=4, columnspan=2, sticky=W+E)

Button(main_window, text="Start", command=start_program).grid(column=0, row=40)
Button(main_window, text="Finish", command=main_window.quit).grid(column=1, row=40, padx=10, pady=10)

Label(main_window, text="Saved Files History:").grid(column=0, row=5, columnspan=2)
history_text_main = Text(main_window, height=10, width=50, state='disabled')
history_text_main.grid(column=0, row=6, columnspan=2, padx=10, pady=5)


main_window.mainloop()
