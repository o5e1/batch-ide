import os
import time
import json
from threading import Thread
from tkinter import Tk, Text, Label, Button, filedialog, messagebox, Toplevel, colorchooser

current_project_path = None
autosave_interval = 30
output_folder = "output"
config_file = "config.json"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def load_settings():
    global editor, output_folder
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            editor.config(bg=config.get('background_color', 'white'))
            output_folder = config.get('output_folder', output_folder)
    else:
        save_settings()

def save_settings():
    global editor, output_folder
    config = {
        'background_color': editor.cget("bg"),
        'output_folder': output_folder
    }
    with open(config_file, 'w') as f:
        json.dump(config, f)

def autosave():
    global autosave_interval
    while True:
        time.sleep(autosave_interval)
        save_code(auto=True)
        update_countdown()

def update_countdown():
    global autosave_interval
    countdown_label.config(text=f"Next autosave in: {autosave_interval} seconds")

def save_code(auto=False):
    global current_project_path
    if current_project_path:
        content = editor.get("1.0", "end-1c")
        project_name = os.path.basename(current_project_path).split('.')[0]
        delete_previous_save(project_name)
        save_path = os.path.join(output_folder, f"{project_name}.bat")
        with open(save_path, "w") as file:
            file.write(content)
        if not auto:
            messagebox.showinfo("Save", f"Project saved as {save_path}")

def delete_previous_save(project_name):
    for file in os.listdir(output_folder):
        if file.startswith(project_name) and file.endswith(".bat"):
            os.remove(os.path.join(output_folder, file))

def load_file():
    global current_project_path
    file_path = filedialog.askopenfilename(defaultextension=".bat", filetypes=[("Batch Files", "*.bat")])
    if file_path:
        current_project_path = file_path
        with open(file_path, "r") as file:
            content = file.read()
        editor.delete("1.0", "end")
        editor.insert("1.0", content)
        highlight_syntax()
        update_filename_label()

def new_project():
    global current_project_path
    current_project_path = filedialog.asksaveasfilename(defaultextension=".bat", filetypes=[("Batch Files", "*.bat")])
    if current_project_path:
        editor.delete("1.0", "end")
        update_filename_label()

def open_settings():
    settings_win = Toplevel(root)
    settings_win.title("Settings")

    Label(settings_win, text="Background Color:").pack(pady=5)
    Button(settings_win, text="Choose Color", command=lambda: choose_background_color(editor)).pack(pady=5)

    Label(settings_win, text="Output Folder:").pack(pady=5)
    Button(settings_win, text="Choose Folder", command=choose_output_folder).pack(pady=5)
    Label(settings_win, text="Current Folder:").pack(pady=5)
    global output_folder_label
    output_folder_label = Label(settings_win, text=output_folder)
    output_folder_label.pack(pady=5)

    Button(settings_win, text="Save Settings", command=lambda: save_settings_and_close(settings_win)).pack(pady=10)

def save_settings_and_close(window):
    global output_folder
    save_settings()
    window.destroy()

def choose_background_color(editor):
    color = colorchooser.askcolor()[1]
    if color:
        editor.config(bg=color)
        save_settings()

def choose_output_folder():
    global output_folder
    new_folder = filedialog.askdirectory()
    if new_folder:
        output_folder = new_folder
        output_folder_label.config(text=output_folder)
        save_settings()

def countdown():
    global autosave_interval
    remaining = autosave_interval
    while True:
        time.sleep(1)
        remaining -= 1
        if remaining <= 0:
            remaining = autosave_interval
        countdown_label.config(text=f"Next autosave in: {remaining} seconds")

def update_filename_label():
    global filename_label
    if current_project_path:
        filename_label.config(text=f"Editing: {os.path.basename(current_project_path)}")
    else:
        filename_label.config(text="No project loaded")

def highlight_syntax():

    keywords = [
    "pip", "echo", "set", "Title", "else", "for", "goto", "call", "pause", 
    "rem", "::", "start", "del", "mkdir", "rmdir", "copy", "move", "exit", 
    "setlocal", "endlocal", "@echo off", "if", "cls"
    ]

    keyword_color = "blue"

    editor.tag_delete("keyword")

    for keyword in keywords:
        start_pos = "1.0"
        while True:
            start_pos = editor.search(keyword, start_pos, stopindex="end", nocase=True, regexp=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(keyword)}c"
            editor.tag_add("keyword", start_pos, end_pos)
            editor.tag_config("keyword", foreground=keyword_color)
            start_pos = end_pos

def on_text_change(event):
    highlight_syntax()

root = Tk()
root.title("Batch++")

editor = Text(root, wrap="none", font=("Courier New", 12), undo=True)
editor.pack(expand=True, fill="both")

filename_label = Label(root, text="No project loaded")
filename_label.pack(side="top", fill="x")

load_settings()

save_button = Button(root, text="Save Project", command=save_code)
save_button.pack(side="left", padx=10)

new_project_button = Button(root, text="New Project", command=new_project)
new_project_button.pack(side="left", padx=10)

load_button = Button(root, text="Load Project", command=load_file)
load_button.pack(side="left", padx=10)

settings_button = Button(root, text="Settings", command=open_settings)
settings_button.pack(side="left", padx=10)

countdown_label = Label(root, text=f"Next autosave in: {autosave_interval} seconds")
countdown_label.pack(side="left", padx=10)

autosave_thread = Thread(target=autosave, daemon=True)
autosave_thread.start()

countdown_thread = Thread(target=countdown, daemon=True)
countdown_thread.start()

editor.bind("<KeyRelease>", on_text_change)
editor.bind("<FocusOut>", highlight_syntax)  

root.mainloop()
