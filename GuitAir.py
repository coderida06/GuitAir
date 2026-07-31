import customtkinter as ctk
from PIL import Image
import cv2
import pygame
from chords import ChordDetector

# --- CustomTkinter GUI Setup ---
ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("1160x580")
app.configure(fg_color="#f3d3d3")
app.title("GuitAir")

app.after(100, lambda: app.wm_state("zoomed"))

# --- OpenCV & Pygame Logic ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

detector = ChordDetector()

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Pre-load sounds
sounds = {
    "Am": pygame.mixer.Sound("chords/chordsound/Am.wav"),
    "C": pygame.mixer.Sound("chords/chordsound/C.wav"),
    "D": pygame.mixer.Sound("chords/chordsound/D.wav"),
    "E": pygame.mixer.Sound("chords/chordsound/E.wav"),
    "Em": pygame.mixer.Sound("chords/chordsound/Em.wav"),
    "F": pygame.mixer.Sound("chords/chordsound/F.wav"),
    "G": pygame.mixer.Sound("chords/chordsound/G.wav"),
    "B": pygame.mixer.Sound("chords/chordsound/B.wav"),
    "Bm": pygame.mixer.Sound("chords/chordsound/Bm.wav"),
    "Dm": pygame.mixer.Sound("chords/chordsound/Dm.wav"),
}

channels = [pygame.mixer.Channel(i) for i in range(4)]
channel_index = 0

video_label = None

# --- Frame Loop for Real-Time Gesture & Sound ---
def update_frame():
    global channel_index

    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame, chord, play_sound = detector.detect(frame)

        # Trigger audio playback when strum/gesture is detected
        if play_sound and chord in sounds:
            channels[channel_index].play(sounds[chord])
            channel_index = (channel_index + 1) % len(channels)

        # Convert OpenCV BGR frame to PIL/CustomTkinter Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_frame)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(640, 480))

        if video_label is not None and video_label.winfo_exists():
            video_label.configure(image=ctk_img)
            video_label.image = ctk_img

    app.after(15, update_frame)

# Clean window destruction
def on_closing():
    cap.release()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

# --- App Pages ---
def show_webcam_page():
    global video_label

    # Clear current UI elements (Logo and Play button)
    for widget in app.winfo_children():
        widget.destroy()

    # Create and position the direct webcam feed label
    video_label = ctk.CTkLabel(app, text="")
    video_label.place(relx=0.5, rely=0.5, anchor="center")

    # Start the continuous frame update loop
    update_frame()

# --- Initial Landing View ---
logo = ctk.CTkImage(
    light_image=Image.open("guitairlogo.png"),
    dark_image=Image.open("guitairlogo.png"),
    size=(500, 500)
)

logo_label = ctk.CTkLabel(
    app,
    image=logo,
    text=""
)
logo_label.place(x=395, y=50)

playbutton = ctk.CTkButton(
    app,
    text="Play",                     
    width=180,                    
    height=80,                    
    corner_radius=40,             
    font=ctk.CTkFont(family="Arial Rounded MT Bold", size=32, weight="bold"), 
    fg_color="#a8090e",          
    hover_color="#f88589",        
    text_color="#ffffff",          
    border_width=4,
    border_color="#f88589",
    command=show_webcam_page
)
playbutton.place(x=550, y=400)

app.mainloop()
