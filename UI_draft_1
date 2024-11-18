#draft under working

import os
import tkinter as tk
from tkinter import filedialog, messagebox

#Server interaction function
def send_command_to_server(command):
    #Server response (server logic piece)
    if "cp" in command:
        return "ACK: File copied successfully."
    elif "rm" in command:
        return "ACK: File deleted."
    elif "ls" in command:
        return "ACK: Listing files...\n[file1.txt, file2.txt, folder1/]"
    elif "mkdir" in command:
        return "ACK: Directory created."
    else:
        return "NACK: Invalid command."

#Function to handle command validation and server interaction
def execute_command():
    command = command_entry.get().strip()
    if not command:
        feedback_text.insert(tk.END, "Error: Command cannot be empty.\n")
        return

    #Basic client-side validation
    if command.startswith("cp"):
        if "server://" in command:
            filepath = command.split("server://")[1].split()[0]
            if "server://" not in command.split()[-1] and not os.path.exists(filepath):
                feedback_text.insert(tk.END, "Error: Local file does not exist.\n")
                return
    elif command.startswith("rm") and "-d" in command:
        filepath = command.split()[-1]
        if os.path.exists(filepath) and not os.path.isdir(filepath):
            feedback_text.insert(tk.END, "Error: Path is not a directory.\n")
            return
    elif command.startswith("mkdir"):
        filepath = command.split()[-1]
        if os.path.exists(filepath):
            feedback_text.insert(tk.END, "Error: Directory already exists.\n")
            return

    #Send command to server and display response
    server_response = send_command_to_server(command)
    feedback_text.insert(tk.END, f"{server_response}\n")

#File dialog to select files
def select_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        command_entry.insert(tk.END, filepath)

#Initialize Tkinter
root = tk.Tk()
root.title("File Management UI")

#Command entry field
command_label = tk.Label(root, text="Enter Command:")
command_label.pack()
command_entry = tk.Entry(root, width=60)
command_entry.pack()

#Action buttons
button_frame = tk.Frame(root)
button_frame.pack()

upload_button = tk.Button(button_frame, text="Upload File", command=lambda: command_entry.insert(0, "cp "))
upload_button.grid(row=0, column=0, padx=5, pady=5)

download_button = tk.Button(button_frame, text="Download File", command=lambda: command_entry.insert(0, "cp server://"))
download_button.grid(row=0, column=1, padx=5, pady=5)

delete_button = tk.Button(button_frame, text="Delete File", command=lambda: command_entry.insert(0, "rm "))
delete_button.grid(row=0, column=2, padx=5, pady=5)

list_button = tk.Button(button_frame, text="List Files", command=lambda: command_entry.insert(0, "ls "))
list_button.grid(row=0, column=3, padx=5, pady=5)

mkdir_button = tk.Button(button_frame, text="Make Directory", command=lambda: command_entry.insert(0, "mkdir "))
mkdir_button.grid(row=0, column=4, padx=5, pady=5)

select_button = tk.Button(button_frame, text="Select File", command=select_file)
select_button.grid(row=0, column=5, padx=5, pady=5)

execute_button = tk.Button(root, text="Execute Command", command=execute_command)
execute_button.pack(pady=10)

#Feedback messages
feedback_label = tk.Label(root, text="Feedback:")
feedback_label.pack()
feedback_text = tk.Text(root, height=10, width=80)
feedback_text.pack()

#Run the UI piece
root.mainloop()
