import tkinter as tk
from tkinter import ttk
import mido

# --- Constants ---
key_to_midi = {'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64, 'F': 65, 'F#': 66, 'G': 67, 'G#': 68, 'A': 69, 'A#': 70, 'B': 71}
major_scale_mapping = {0: '1', 2: '2', 4: '3', 5: '4', 7: '5', 9: '6', 11: '7'}

# --- Global Variables ---
last_note = None
inport = None

# --- Utility Functions ---
def get_device_names():
    all_devices = mido.get_input_names()
    device_status = []
    for device in all_devices:
        try:
            test_port = mido.open_input(device)
            test_port.close()
            device_status.append(device)
        except:
            device_status.append(f"<<IN USE>> - {device}")
    return device_status

def refresh_midi_list():
    device_names = get_device_names()
    device_combobox['values'] = device_names

# --- Event Handlers ---
def on_midi_message(msg):
    global last_note
    root_key = key_to_midi[root_key_combobox.get()]
    note = msg.note - root_key
    note_mod_12 = note % 12
    if msg.type == 'note_on':
        last_note = msg.note
        if note_mod_12 in major_scale_mapping:
            display_var.set(major_scale_mapping[note_mod_12])
        else:
            display_var.set(major_scale_mapping.get(note_mod_12, get_sharp_display(note_mod_12)))
    elif msg.type == 'note_off' and not remain_displayed_var.get() and last_note == msg.note:
        display_var.set("")

def select_midi_device(event):
    global inport
    device_name = device_combobox.get()
    if "(In use)" in device_name:
        print("Device is in use. Can't be selected.")
        return
    if inport:
        inport.close()
    inport = mido.open_input(device_name, callback=on_midi_message)
    show_optional_widgets()

def clear_display():
    if not remain_displayed_var.get():
        display_var.set("")

def get_sharp_display(note_mod_12):
    closest_below = max(k for k in major_scale_mapping if k < note_mod_12)
    return f"{major_scale_mapping[closest_below]}#" if off_scale_var.get() == "Sharp" else f"{major_scale_mapping[closest_below + 2]}b"

# --- UI Elements ---
def show_optional_widgets():
    root_key_label.pack(side='top')
    root_key_combobox.pack(side='top')
    remain_displayed_check.pack(side='top', pady=(10, 0))
    off_scale_label.pack(side='top', pady=(10, 0))
    off_scale_radio_sharp.pack(side='top')
    off_scale_radio_flat.pack(side='top')
    nash_display.pack(side='bottom', anchor='center', pady=(0, 100))

# --- Initialize UI ---
root = tk.Tk()
root.geometry('550x800')
root.title('MIDI Nashville Numbers')
root.configure(bg='white')

# Remaining UI elements
display_var = tk.StringVar()
nash_display = tk.Label(root, textvariable=display_var, font=("Helvetica", 200, "bold"), bg='white')
remain_displayed_var = tk.IntVar(value=0)
remain_displayed_check = tk.Checkbutton(root, text="Number Remains Displayed with Key Release", variable=remain_displayed_var, command=clear_display, bg='white', activebackground='white')
off_scale_var = tk.StringVar(value="Sharp")
off_scale_label = tk.Label(root, text="Off-scale label:", bg='white')
off_scale_radio_sharp = tk.Radiobutton(root, text="Sharp", variable=off_scale_var, value="Sharp", bg='white', activebackground='white')
off_scale_radio_flat = tk.Radiobutton(root, text="Flat", variable=off_scale_var, value="Flat", bg='white', activebackground='white')
root_key_label = tk.Label(root, text="Root Key:", bg='white')
root_key_combobox = ttk.Combobox(root, values=list(key_to_midi.keys()))
root_key_combobox.current(0)
midi_device_label = tk.Label(root, text="Select MIDI Device to use:", bg='white')
midi_device_label.pack(side='top')

# Dropdown for device selection
device_names = get_device_names()
device_combobox = ttk.Combobox(root, values=device_names, width=50)
device_combobox.pack(side='top')
device_combobox.bind('<<ComboboxSelected>>', select_midi_device)

# Refresh MIDI List Button
refresh_button = tk.Button(root, text="Refresh MIDI List", command=refresh_midi_list, bg='white', activebackground='white')
refresh_button.pack(side='top', pady=(10, 10))

root.mainloop()
