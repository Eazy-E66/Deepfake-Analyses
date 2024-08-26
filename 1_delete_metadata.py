import pandas as pd
import tkinter as tk
from tkinter import filedialog

def confirm_action(prompt):
    while True:
        response = input(prompt + " (y/n): ").strip().lower()
        if response in ['y', 'n']:
            return response == 'y'
        print("Invalid input, please enter 'y' or 'n'.")

def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

def delete_columns(df, columns):
    existing_columns = [col for col in columns if col in df.columns]
    if confirm_action(f"Do you want to delete the columns: {', '.join(existing_columns)}?"):
        df = df.drop(columns=existing_columns)
        print(f"Columns {', '.join(existing_columns)} deleted successfully.")
        return df
    else:
        print(f"Skipping deletion of columns: {', '.join(columns)}.")
        return df

def main():
    file_path = select_csv_file()
    if not file_path:
        return
    
    df = pd.read_csv(file_path)
    print("CSV file read successfully.")
    print("Initial DataFrame:")
    print(df.head())  # Show the initial part of the DataFrame for confirmation
    
    initial_columns_to_delete = ["StartDate", "EndDate", "Status", "IPAddress", "Progress", "Duration (in seconds)"]
    df = delete_columns(df, initial_columns_to_delete)
    
    additional_columns_to_delete = ["RecordedDate", "ResponseId", "RecipientLastName", "RecipientFirstName", 
                                    "RecipientEmail", "ExternalReference", "LocationLatitude", "LocationLongitude", 
                                    "DistributionChannel", "UserLanguage"]
    df = delete_columns(df, additional_columns_to_delete)

    print("Modified DataFrame:")
    print(df.head())  # Show the modified part of the DataFrame for confirmation
    
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Modified CSV file saved to {save_path}")
    else:
        print("File save cancelled.")

if __name__ == "__main__":
    main()
