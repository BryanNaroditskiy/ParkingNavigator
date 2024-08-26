import tkinter as tk
from tkinter import messagebox
import json
import os

def save_data():
    try:
        # Validate and get input data
        row_number = int(row_entry.get())
        space_number = int(space_entry.get())
        tl_coords = tl_entry.get().split(',')
        if len(tl_coords) != 2:
            raise ValueError("Coordinate pair should have two values")
        x, y = float(tl_coords[0].strip()), float(tl_coords[1].strip())

        br_coords = br_entry.get().split(',')
        if len(br_coords) != 2:
            raise ValueError("Coordinate pair should have two values")
        x2, y2 = float(br_coords[0].strip()), float(br_coords[1].strip())

        # New entry
        new_entry = {
            "row_number": row_number,
            "space_number": space_number,
            "tl_coordinates": {"x": x, "y": y},
            "br_coordinates": {"x": x2, "y": y2}
        }

        # File path
        file_path = 'img_data.json'

        # Check if the JSON file exists and read data
        if os.path.isfile(file_path):
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
            if "Woodland" not in data:
                data["Woodland"] = []
        else:
            data = {"Woodland": []}

        # Check if the same row and space number exist
        if any(entry["row_number"] == row_number and entry["space_number"] == space_number for entry in data["Woodland"]):
            messagebox.showerror("Error", "An entry with the same row and space number already exists.")
            return

        # Append new data
        data["Woodland"].append(new_entry)

        # Save updated data to JSON
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        messagebox.showinfo("Success", "Data saved successfully")

    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")



# Set up the Tkinter window
root = tk.Tk()
root.title("Data Entry")

# Create labels and entry widgets
tk.Label(root, text="Row Number:").grid(row=0, column=0)
row_entry = tk.Entry(root)
row_entry.grid(row=0, column=1)

tk.Label(root, text="Space Number:").grid(row=1, column=0)
space_entry = tk.Entry(root)
space_entry.grid(row=1, column=1)

# Coordinate entry fields
tk.Label(root, text="Top-Left (TL):").grid(row=2, column=0)
tl_entry = tk.Entry(root)
tl_entry.grid(row=2, column=1)

tk.Label(root, text="Bottom-Right (BR):").grid(row=3, column=0)
br_entry = tk.Entry(root)
br_entry.grid(row=3, column=1)

# Create a save button
save_button = tk.Button(root, text="Save Data", command=save_data)
save_button.grid(row=4, columnspan=2)

# Run the application
root.mainloop()
