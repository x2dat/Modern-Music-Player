import os
import threading
import time
from tkinter import *
from tkinter import filedialog
import tkinter as tk
from colorama import Fore
from mutagen.mp3 import MP3
from pygame import mixer

mixer.init()

# Store the current position of the music
current_position = 0
paused = False
selected_folder_path = ""  # Store the selected folder path
selected_song_length = 0  # Store the length of the selected song

def update_progress():
    global current_position, paused
    while True:
        if mixer.music.get_busy() and not paused:
            current_position = mixer.music.get_pos() / 1000

            # Check if the current song has reached its maximum duration
            if current_position >= selected_song_length:
                play_next_song()

            current_time = time.strftime('%M:%S', time.gmtime(current_position))
            time_label.config(text=f"Time Elapsed: {current_time}")

            remaining_time = time.strftime('%M:%S', time.gmtime(selected_song_length - current_position))
            remaining_time_label.config(text=f"Time Left: {remaining_time}")

            # Update the length indicators
            white_length_indicator.config(width=int(current_position / selected_song_length * 300))
            gray_length_indicator.config(width=300 - int(current_position / selected_song_length * 300))

            window.update()
        time.sleep(0.1)

def play_next_song():
    current_selection = lbox.curselection()
    if current_selection:
        current_index = current_selection[0]
        next_index = (current_index + 1) % lbox.size()
        lbox.selection_clear(0, tk.END)  # Deselect all
        lbox.selection_set(next_index)  # Select the next song
        lbox.activate(next_index)  # Activate the next song
        play_music()

def play_music():
    global paused, current_position, selected_song_length
    if not paused:
        if len(lbox.curselection()) > 0:
            selected_song = lbox.get(lbox.curselection())
            song_path = os.path.join(selected_folder_path, selected_song)
            audio = MP3(song_path)
            selected_song_length = audio.info.length
            mixer.music.load(song_path)
            mixer.music.play(start=current_position)  # Start from the paused position
            paused = True
    else:
        mixer.music.unpause()
        paused = False

def select_music_folder():
    global selected_folder_path
    selected_folder_path = filedialog.askdirectory()
    if selected_folder_path:
        lbox.delete(0, tk.END)
        for filename in os.listdir(selected_folder_path):
            if filename.endswith(".mp3"):
                lbox.insert(tk.END, filename)  # Insert only the filename, not the full path
        print(Fore.LIGHTGREEN_EX, "Folder selected", Fore.LIGHTWHITE_EX)

def stop_music():
    global paused, current_position
    if mixer.music.get_busy():
        mixer.music.pause()
        paused = True
        current_position = mixer.music.get_pos() / 1000
    else:
        paused = False

def on_spacebar(event):
    play_music()

# Create the main window
window = Tk()
window.title("Music Player")
window.geometry("600x400")
window.configure(bg='black')  # Set background color
window.resizable(False, False)

# Create a label for the time elapsed and remaining time
time_label = Label(window, text="Time Elapsed: 00:00", bg='black', fg='white')
time_label.pack(pady=5)

remaining_time_label = Label(window, text="Time Left: 00:00", bg='black', fg='white')
remaining_time_label.pack(pady=5)

# Create a canvas for the length indicators
length_indicators_frame = Frame(window, bg='black')
length_indicators_frame.pack(pady=10)

# White length indicator
white_length_indicator = Canvas(length_indicators_frame, bg='white', width=0, height=10)
white_length_indicator.pack(side=LEFT)

# Gray length indicator
gray_length_indicator = Canvas(length_indicators_frame, bg='gray', width=300, height=10)
gray_length_indicator.pack(side=LEFT)

# Create a listbox to display the available songs in the selected folder
lbox = Listbox(window, height=10, width=60, bg='black', fg='white', selectbackground='gray', selectforeground='white', activestyle='none', bd=0, relief='solid', highlightthickness=1, highlightcolor='gray')
lbox.pack(pady=10)

# Function to make buttons truly round
def round_button(widget):
    widget.config(relief='flat', bd=0, overrelief="groove", highlightthickness=2)

button_frame = tk.Frame(window, bg='black')

play_button = Button(button_frame, text="Play", command=play_music, bg='gray', fg='white', padx=10, pady=5)
play_button.pack(side=tk.LEFT, padx=10)
round_button(play_button)

select_folder_button = Button(button_frame, text="Select Music Folder", command=select_music_folder, bg='gray', fg='white', padx=10, pady=5)
select_folder_button.pack(side=tk.LEFT, padx=10)
round_button(select_folder_button)

stop_button = Button(button_frame, text="Pause", command=stop_music, bg='gray', fg='white', padx=10, pady=5)
stop_button.pack(side=tk.LEFT, padx=10)
round_button(stop_button)

button_frame.pack(pady=10)

# Bind the spacebar key to play/pause
window.bind("<space>", on_spacebar)

# Create a thread to update the progress bar and time labels
pt = threading.Thread(target=update_progress)
pt.daemon = True
pt.start()

window.mainloop()
