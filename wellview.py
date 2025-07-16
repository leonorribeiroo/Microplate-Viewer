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
    '96-well plate': [0, 49.45, 91.66, 106.88, 149.06, 161.56, 203.75, 217.91, 260.09, 274.22,
                      316.41, 330.56, 372.75, 386.25, 428.44, 442.59, 484.78],
    '48-well plate': [0, 78, 138, 153, 214, 228, 290, 302, 366, 377, 442, 452, 518],
    '24-well plate': [0, 85.16, 172.5, 198.84, 286.18, 312.53, 399.87, 426.09, 513.43]
}

pxCo_dict = {
    '96-well plate': [0, 68.99, 111.13, 125.27, 167.42, 181.25, 223.4, 237.5, 279.65, 293.75,
                      335.9, 350.04, 392.19, 406.33, 448.48, 462.62, 504.77, 518.87, 561.02,
                      575.16, 617.31, 631.45, 673.6, 687.73, 729.88],
    '48-well plate': [0, 98.24, 156.6, 182.91, 241.27, 267.58, 325.94, 352.25,
                      410.61, 436.92, 495.28, 521.59, 579.95, 606.26, 664.62, 690.93, 749.29],
    '24-well plate': [0, 96.23, 183.59, 208.96, 296.32, 321.69, 409.05, 434.42,
                      521.78, 547.15, 634.51, 659.88, 747.24]
}

preview_process = None 

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
    img_path = f"{pltSel.replace('-well plate', '')}-Well_plate.jpg"
    
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
    image_window.geometry("1920x1080")
    image_window.title("Microplate Viewer")
    
    top_frame = Frame(image_window)
    top_frame.pack(fill="x")
    
    # Add the I3Slogo
    logo_image = Image.open("logo2.png")
    logo_image = logo_image.resize((300, 145))  
    logo_tk = ImageTk.PhotoImage(logo_image)
    logo_label = Label(image_window, image=logo_tk)
    logo_label.place(relx=0.0, rely=0.0, anchor="nw", y=-25)

    Label(top_frame, text="Select the well to capture", font=("Arial", 24, "bold")).pack()
    Label(top_frame, text=f"User: {userNm}", font=("Arial", 16)).pack()
    Label(top_frame, text=f"Microplate ID: {plateNm}", font=("Arial", 16)).pack()

    content_frame = Frame(image_window)
    content_frame.pack(fill="both", expand=True)

    image_frame = Frame(content_frame)
    image_frame.pack(side="left", padx=40, pady=20)

    img_pil = Image.fromarray(img_cv)
    width, height = img_pil.size
    canvas = Canvas(image_frame, width=width, height=height, bg="white", highlightthickness=0)
    canvas.pack()

    right_frame = Frame(content_frame, width=300)
    right_frame.pack(side="left", fill="y",padx=40 , pady=20, anchor="n")

    history_frame = Frame(right_frame)
    history_frame.pack(pady=10, fill="x")

    canvas.create_image(0, 0, anchor="nw", image=img_tk)

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

    preview_button_frame = Frame(history_frame)
    preview_button_frame.grid(row=4, column=0, columnspan=3, pady=5)

    # Function to preview camera
    def preview_camera():
        global preview_process
        try:
            preview_process = subprocess.Popen(["libcamera-hello", "-t", "0", "--hflip", "--vflip"])
        except subprocess.CalledProcessError as e:
            print(f"Error during camera preview: {e}")
    Button(preview_button_frame, text="Start Preview", command=preview_camera).pack(side="left", padx=10)


    def stop_preview():
        global preview_process
        if preview_process and preview_process.poll() is None:
            preview_process.terminate()
            preview_process.wait()
            preview_process = None
    Button(preview_button_frame, text="Close Preview", command=stop_preview).pack(side="left", padx=10)


    # Function to handle the click event on a well
    def click_canvas(event):
        global img_cv, img_pil, img_tk
        x, y = event.x, event.y
        pxCo = pxCo_dict[pltSel]
        pxRo = pxRo_dict[pltSel]

        iCo = bisect(pxCo, x)
        iRo = bisect(pxRo, y)

        if iCo > 0 and iRo > 0 and iCo % 2 == 0 and iRo % 2 == 0:
            strg = 'ABCDEFGH'
            well_id = strg[int(iRo/2 - 1)] + str(int(iCo/2))

            current_magnification = magnification.get()

            # Update the history
            history_text.config(state='normal')
            history_text.insert('end', f"{datetime.now().strftime('%H:%M:%S')} - {current_magnification} - {well_id}\n")
            history_text.config(state='disabled')

            # Copy and draw label at center of correct well
            img_display = img_cv.copy()
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = well_id

            if pltSel == '96-well plate':
                font_scale = 0.6
                thickness = 2
            else:
                font_scale = 1
                thickness = 2

            x_center = (pxCo[iCo - 1] + pxCo[iCo]) // 2
            y_center = (pxRo[iRo - 1] + pxRo[iRo]) // 2

            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = int(x_center - text_size[0] / 2)
            text_y = int(y_center + text_size[1] / 2)

            cv2.putText(img_display, text, (text_x, text_y), font, font_scale, (255, 0, 0), thickness)


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

                file_name = os.path.join(folderpath, f"{current_datetime}_{well_id}_{current_magnification}.png")

                try:
                    subprocess.run(["libcamera-still", "--hflip", "--vflip", "-e", "png", "-o", file_name], check=True)
                    print(f"Image captured and saved: {file_name}")
                    
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
main_window.title('WellView')
main_window.columnconfigure(0, weight=1)
main_window.columnconfigure(1, weight=1)

# Add the i3S logo 
logo_image = Image.open("logo.png")
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
plate_list = ["96-well plate", "48-well plate", "24-well plate"]
plate_value = StringVar(main_window)
plate_value.set("Select a microplate type")
OptionMenu(main_window, plate_value, *plate_list).grid(column=0, row=4, columnspan=2, sticky=W+E)

Button(main_window, text="Start", command=start_program).grid(column=0, row=40)
Button(main_window, text="Finish", command=main_window.quit).grid(column=1, row=40, padx=10, pady=10)

Label(main_window, text="Saved Files History:").grid(column=0, row=5, columnspan=2)
history_text_main = Text(main_window, height=10, width=50, state='disabled')
history_text_main.grid(column=0, row=6, columnspan=2, padx=10, pady=5)


main_window.mainloop()
