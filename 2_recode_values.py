import pandas as pd
import tkinter as tk
from tkinter import filedialog
import json

def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

def display_column_info(df, column_name):
    print(f"\nColumn: {column_name}")
    print("Header and first two rows for context:")
    print(df[[column_name]].head(3))

def display_unique_values(df, column_name):
    unique_values = df[column_name].unique()
    print(f"\nUnique values in column '{column_name}':")
    for value in unique_values:
        print(value)

def confirm_action(prompt):
    while True:
        response = input(prompt + " (y/n/ap): ").strip().lower()
        if response in ['y', 'n', 'ap']:
            return response
        print("Invalid input, please enter 'y', 'n', or 'ap'.")

def get_recode_mapping():
    mapping = {}
    while True:
        old_value = input("Enter the value to be replaced (or type 'done' to finish): ").strip()
        if old_value.lower() == 'done':
            break
        new_value = input(f"Enter the new value for {old_value}: ").strip()
        mapping[old_value] = new_value
    return mapping

def recode_column(df, column_name, mapping):
    df[column_name] = df[column_name].replace(mapping)
    return df

def save_recode_mappings(mappings):
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as f:
            json.dump(mappings, f)
        print(f"Recode mappings saved to {file_path}")
    else:
        print("Saving recode mappings cancelled.")

def load_recode_mappings():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as f:
            mappings = json.load(f)
        print(f"Recode mappings loaded from {file_path}")
        return mappings
    else:
        print("Loading recode mappings cancelled.")
        return None

def apply_recode_mappings(df, mappings):
    for column, mapping in mappings.items():
        if column in df.columns:
            df = recode_column(df, column, mapping)
            print(f"Recode mapping applied to column '{column}'.")
        else:
            print(f"Column '{column}' not found in the DataFrame.")
    return df

def main():
    load_choice = input("Do you want to load recode mappings from a file? (y/n): ").strip().lower()
    if load_choice == 'y':
        recode_mappings = load_recode_mappings()
        if recode_mappings is None:
            return
    else:
        recode_mappings = {}

    file_path = select_csv_file()
    if not file_path:
        return
    
    df = pd.read_csv(file_path)
    print("CSV file read successfully.")
    
    if recode_mappings:
        df = apply_recode_mappings(df, recode_mappings)
        print("Loaded recode mappings have been applied.")
    else:
        previous_mapping = None

        for column in df.columns:
            display_column_info(df, column)
            display_unique_values(df, column)
            
            action = confirm_action("Do you want to recode values in this column?")
            if action == 'y':
                recode_mapping = get_recode_mapping()
                df = recode_column(df, column, recode_mapping)
                previous_mapping = recode_mapping
                recode_mappings[column] = recode_mapping
                print(f"Values in column '{column}' have been recoded.")
            elif action == 'ap' and previous_mapping is not None:
                df = recode_column(df, column, previous_mapping)
                recode_mappings[column] = previous_mapping
                print(f"Previous recoding applied to column '{column}'.")
            else:
                print(f"Skipping column '{column}'.")

        save_choice = input("Do you want to save the recode mappings? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_recode_mappings(recode_mappings)
    
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Modified CSV file saved to {save_path}")
    else:
        print("File save cancelled.")

if __name__ == "__main__":
    main()