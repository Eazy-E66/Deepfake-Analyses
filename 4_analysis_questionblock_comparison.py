import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import tkinter as tk
from tkinter import filedialog

# Mappings
mapping_questions = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Somewhat disagree",
    4: "Neither [...]",
    5: "Somewhat agree",
    6: "Agree",
    7: "Strongly agree"
}

mapping_share = {
    1: "Extremely unlikely",
    2: "Moderately unlikely",
    3: "Slightly unlikely",
    4: "Neither [...]",
    5: "Slightly likely",
    6: "Moderately likely",
    7: "Extremely likely"
}

# label_map = {
#     '__1': '__real?',
#     '__2': '__credible?',
#     '__3': '__deepfake?',
#     '_share': '_sharing intention'
# }

# File explorer
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

# Filter out non-deepfake columns and separate Trump and Biden columns
def filter_and_separate_columns(df):
    # Exclude Trump_Bonus (real video)
    columns_to_exclude = [col for col in df.columns if 'Trump_Bonus' in col]
    df_filtered = df.drop(columns=columns_to_exclude)
    
    # Separate Trump and Biden columns
    biden_columns = [col for col in df_filtered.columns if 'Biden' in col]
    trump_columns = [col for col in df_filtered.columns if 'Trump' in col and 'Bonus' not in col]
    
    return df_filtered, biden_columns, trump_columns

# Calculate means, medians, and perform t-tests
def calculate_means_and_ttests(df, biden_columns, trump_columns):
    results = {}
    
    for question in ['__1', '__2', '__3', '_share']:
        biden_responses = df[biden_columns].filter(like=question).values.flatten()
        trump_responses = df[trump_columns].filter(like=question).values.flatten()
        
        # Calculate means and medians
        biden_mean = np.nanmean(biden_responses)
        trump_mean = np.nanmean(trump_responses)
        biden_median = np.nanmedian(biden_responses)
        trump_median = np.nanmedian(trump_responses)
        
        # Perform t-test
        t_stat, p_val = ttest_ind(biden_responses, trump_responses, nan_policy='omit')
        results[question] = {'biden_mean': biden_mean, 'trump_mean': trump_mean, 'biden_median': biden_median, 'trump_median': trump_median, 'p_val': p_val}
    
    return results

def print_results(results):
    print("Question & Biden Mean & Trump Mean & Biden Median & Trump Median & p-value")
    for question, result in results.items():
        question_label = question.replace('__', '').replace('_', '')
        biden_mean = result['biden_mean']
        trump_mean = result['trump_mean']
        biden_median = result['biden_median']
        trump_median = result['trump_median']
        p_val = result['p_val']
        print(f"{question_label} & {biden_mean:.2f} & {trump_mean:.2f} & {biden_median:.2f} & {trump_median:.2f} & {p_val:.4f}")

# Plot combined boxplots for both Biden and Trump
def plot_combined_boxplots(df, biden_columns, trump_columns, results):
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Prepare data for each boxplot
    all_data = []
    labels = [
        'Biden\n__real?', 'Trump\n__real?',
        'Biden\n__credible?', 'Trump\n__credible?',
        'Biden\n__deepfake?', 'Trump\n__deepfake?',
        'Biden\n_sharing\nintention', 'Trump\n_sharing\nintention'
    ]
    for question in ['__1', '__2', '__3', '_share']:
        biden_data = df[biden_columns].filter(like=question).values.flatten()
        trump_data = df[trump_columns].filter(like=question).values.flatten()
        all_data.extend([biden_data, trump_data])
        #question_label = label_map.get(question, question)
        #labels.extend([f'Biden{question_label}', f'Trump{question_label}'])

    # Custom boxplot
    meanprops = dict(color='red', linewidth=1, linestyle='-')
    boxplot = ax1.boxplot(all_data, patch_artist=True, showmeans=True, meanline=True, meanprops=meanprops)

    # Custom styling
    for box in boxplot['boxes']:
        box.set(color='lightblue', linewidth=2)
        box.set(facecolor='lightblue')
    for median in boxplot['medians']:
        median.set(color='orange', linewidth=2)
    for whisker in boxplot['whiskers']:
        whisker.set(color='black', linewidth=1)
    for cap in boxplot['caps']:
        cap.set(color='black', linewidth=1)
    for flier in boxplot['fliers']:
        flier.set(marker='o', color='lightblue', alpha=0.5)

    # Set x-axis labels and rotate them for clarity
    ax1.set_xticklabels(labels, rotation=0, ha='center', fontsize=14)
    
    # Highlight "sharing intention" blocks
    for i, tick in enumerate(ax1.get_xticklabels()):
        if 'sharing intention' in tick.get_text():
            tick.set_color('darkblue')
    
    # Settings for y-axis labels
    ax1.set_yticks(range(1, 8))
    ax1.set_yticklabels([f'{mapping_questions[i].replace(" ", "\n")}: {i}' for i in range(1, 8)], color='black', fontsize=14)

    # Settings for secondary y-axis labels
    ax2 = ax1.twinx()
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_yticks(range(1, 8))
    ax2.set_yticklabels([f'{i}: {mapping_share[i].replace(" ", "\n")}' for i in range(1, 8)], color='darkblue', fontsize=14)

    # Add vertical lines between question types
    ax1.axvline(x=2.5, color='black', linestyle='-', linewidth=0.5)
    ax1.axvline(x=4.5, color='black', linestyle='-', linewidth=0.5) 

    # Add a vertical dashed line to separate "sharing intention"
    ax1.axvline(x=6.5, color='darkblue', linestyle='--')

    # Add grid lines for every y-tick
    ax1.yaxis.grid(True)

    # Add legend for median, mean, and outliers
    handles = [
        plt.Line2D([0], [0], color='orange', linewidth=2, label='Median'),
        plt.Line2D([0], [0], color='red', linewidth=2, label='Mean'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=8, label='Outliers')
    ]
    ax1.legend(handles=handles, loc='upper left')

    y_position = [5.5, 5.5, 6.5, 6.5]  # Adjust y-positions for significance
    for i, (question, ypos) in enumerate(zip(['__1', '__2', '__3', '_share'], y_position)):
        p_val = results[question]['p_val']
        significance = '*' if p_val < 0.05 else 'ns'
        ax1.text(1.5 + 2*i, ypos, f'p={p_val:.4f} ({significance})', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    plt.show()

def main():
    file_path = select_file()
    if file_path is None:
        exit()

    df = pd.read_csv(file_path, skiprows=[1, 2])
    
    # Filter for finished responses
    df_filtered = df[df['Finished'] == 1]
    
    # Filter columns and separate by deepfake type
    df_filtered, biden_columns, trump_columns = filter_and_separate_columns(df_filtered)
    
    # Calculate means, medians, and perform t-tests
    results = calculate_means_and_ttests(df_filtered, biden_columns, trump_columns)
    
    # Print results in LaTeX-friendly format
    print_results(results)
    
    # Plot combined boxplots for Biden and Trump
    plot_combined_boxplots(df_filtered, biden_columns, trump_columns, results)

if __name__ == "__main__":
    main()
