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
    # Initialize tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open file dialog
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],  # Filter for JSON files
        title="Select a JSON file"
    )

    if not file_path:
        print("No file selected.")
        return None

    return file_path

# Prepare data for regression using NumPy arrays
def prepare_data(data):
    credibility_data = []
    ideology_data = []
    stance_data = []

    # Loop through each key-value pair in the JSON data
    for key, values in data.items():
        ideology = 1 if 'Biden' in key else 0  # 1 for Biden (left-leaning), 0 for Trump (right-leaning)
        stance = 1 if '1X' in key else 0  # 1 for Left stance, 0 for Right stance

        # Add data to lists
        credibility_data.extend(values)
        ideology_data.extend([ideology] * len(values))
        stance_data.extend([stance] * len(values))

    # Convert lists to NumPy arrays and enforce integer type
    credibility_array = np.array(credibility_data, dtype=int)
    ideology_array = np.array(ideology_data, dtype=int)
    stance_array = np.array(stance_data, dtype=int)

    # Create interaction term
    interaction_array = ideology_array * stance_array

    # Stack independent variables into a 2D array for regression
    X = np.column_stack((ideology_array, stance_array, interaction_array))
    
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

def plot_side_by_side(model, X):
    # Extract coefficients
    beta_0, beta_1, beta_2, beta_3 = model.params

    # Define stances and political ideologies
    stances = ['Left', 'Right']
    ideologies = ['Left-Leaning', 'Neutral', 'Right-Leaning']
    stance_values = [1, 0]  # 1 for Left, 0 for Right
    ideology_values = [1, 0, -1]  # 1 for Left-Leaning, 0 for Neutral, -1 for Right-Leaning

    # Calculate predicted values for each combination
    predictions = []

    for stance_val in stance_values:
        stance_predictions = []
        for ideology_val in ideology_values:
            interaction_term = ideology_val * stance_val
            predicted_credibility = (beta_0 +
                                     beta_1 * ideology_val +
                                     beta_2 * stance_val +
                                     beta_3 * interaction_term)
            stance_predictions.append(predicted_credibility)
        predictions.append(stance_predictions)

    # Convert predictions to a NumPy array for easier slicing
    predictions = np.array(predictions)

    # Create the figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Interaction Plot
    for i, ideology in enumerate(ideologies):
        linestyle = 'dashed' if ideology == 'Neutral' else 'solid'
        color = 'red' if ideology == 'Neutral' else 'lightblue' if ideology == 'Left-Leaning' else 'orange'
        ax1.plot(stances, predictions[:, i], marker='o', label=ideology, linestyle=linestyle, color=color)
    
    ax1.set_xlabel('Video Stance', fontsize=14)
    ax1.set_ylabel('Predicted Credibility', fontsize=14)
    ax1.set_title('Interaction Plot', fontsize=16)
    ax1.legend(fontsize=15)
    ax1.set_ylim(1, 7)
    ax1.grid(True, axis='y', linestyle='-', linewidth=0.5)
    ax1.tick_params(axis='y', labelsize=14)

    # Facet Grid (Grouped Bar Plot)
    index = np.arange(len(stances))
    bar_width = 0.2

    ax2.bar(index - bar_width, predictions[:, 0], bar_width, label='Left-Leaning', color='lightblue')
    ax2.bar(index, predictions[:, 1], bar_width, label='Neutral', color='red', hatch='//', linestyle='dashed')
    ax2.bar(index + bar_width, predictions[:, 2], bar_width, label='Right-Leaning', color='orange')

    ax2.set_xlabel('Video Stance', fontsize=14)
    ax2.set_title('Grouped Bar Plot', fontsize=16)
    ax2.set_xticks(index)
    ax2.set_xticklabels(stances, fontsize=14)
    ax2.set_ylim(1, 7)
    ax2.legend(fontsize=15)
    ax2.grid(True, axis='y', linestyle='-', linewidth=0.5)
    ax2.tick_params(axis='y', labelsize=14)
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

    # Plot side-by-side visualizations
    plot_side_by_side(model, X)

if __name__ == "__main__":
    main()
