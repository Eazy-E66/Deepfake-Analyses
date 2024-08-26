import json
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Function to load JSON data from a file path
def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to select a JSON file using tkinter file dialog
def select_json_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")], title="Select a JSON file"
    )
    if not file_path:
        print("No file selected.")
        return None
    return file_path

# Prepare data for regression using NumPy arrays
def prepare_data(data):
    credibility_data = []
    politician_data = []
    stance_data = []

    for key, values in data.items():
        politician = 1 if 'Biden' in key else 0  # 1 for Biden, 0 for Trump
        stance = 1 if '1X' in key else 0  # 1 for Left stance, 0 for Right stance

        # Add data to lists
        credibility_data.extend(values)
        politician_data.extend([politician] * len(values))
        stance_data.extend([stance] * len(values))

    # Convert lists to NumPy arrays and enforce integer type
    credibility_array = np.array(credibility_data, dtype=int)
    politician_array = np.array(politician_data, dtype=int)
    stance_array = np.array(stance_data, dtype=int)

    # Create interaction term
    interaction_array = politician_array * stance_array

    # Stack independent variables into a 2D array for regression
    X = np.column_stack((politician_array, stance_array, interaction_array))
    
    # Add a constant to the independent variables
    X = sm.add_constant(X)

    # The dependent variable
    y = credibility_array

    return X, y

# Perform regression analysis using Statsmodels
def perform_regression(X, y):
    # Fit the regression model
    model = sm.OLS(y, X).fit()
    return model

# Function to create a side-by-side plot with Interaction Plot and Facet Grid (Grouped Bar Plot)
def plot_side_by_side(model, X):
    # Extract coefficients
    beta_0, beta_1, beta_2, beta_3 = model.params

    # Create combinations
    stances = ['Left', 'Right']
    politicians = ['Biden', 'Trump']
    stance_values = [1, 0]  # 1 for Left, 0 for Right
    politician_values = [1, 0]  # 1 for Biden, 0 for Trump

    # Predicted values for each combination
    predictions = []

    for stance, stance_val in zip(stances, stance_values):
        for politician, politician_val in zip(politicians, politician_values):
            interaction_term = politician_val * stance_val
            predicted_credibility = (beta_0 + 
                                     beta_1 * politician_val + 
                                     beta_2 * stance_val + 
                                     beta_3 * interaction_term)
            predictions.append(predicted_credibility)

    # Create the figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Interaction Plot
    for i, politician in enumerate(politicians):
        ax1.plot(stances, predictions[i*2:(i+1)*2], marker='o', label=politician, color='lightblue' if politician == 'Biden' else 'orange')
    ax1.set_xlabel('Stance', fontsize=14)
    ax1.set_ylabel('Predicted Credibility', fontsize=14)
    ax1.set_title('Interaction Plot', fontsize=16)
    ax1.legend(fontsize=15)
    ax1.set_ylim(1, 7)
    ax1.grid(True, axis='y', linestyle='-', linewidth=0.5)
    ax1.tick_params(axis='y', labelsize=14)  # Set y-tick label size

    # Facet Grid (Grouped Bar Plot)
    index = np.arange(len(stances))
    bar_width = 0.35
    ax2.bar(index, predictions[:2], bar_width, label='Biden', color='lightblue')
    ax2.bar(index + bar_width, predictions[2:], bar_width, label='Trump', color='orange')
    ax2.set_xlabel('Stance', fontsize=14)
    ax2.set_title('Facet Grid (Grouped Bar Plot)', fontsize=16)
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels(stances, fontsize=14)
    ax2.set_ylim(1, 7)
    ax2.legend(fontsize=15)
    ax2.grid(True, axis='y', linestyle='-', linewidth=0.5)
    ax2.tick_params(axis='y', labelsize=14)  # Set y-tick label size
    ax2.yaxis.label.set_visible(False)  # Hide y-axis label

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()

def main():
    # Use tkinter to select a JSON file
    json_file_path = select_json_file()
    
    if json_file_path is None:
        print("File selection was cancelled.")
        return

    # Load data from the selected JSON file
    data = load_data_from_json(json_file_path)
    
    # Prepare data for regression
    X, y = prepare_data(data)
    
    # Perform regression
    model = perform_regression(X, y)
    
    # Print regression results
    print(model.summary())

    # Plot Interaction Plot and Facet Grid Plot side by side
    plot_side_by_side(model, X)

if __name__ == "__main__":
    main()
