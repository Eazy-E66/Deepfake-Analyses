import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Mappings (as before)
mapping_questions = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Somewhat disagree",
    4: "Neither agree nor disagree",
    5: "Somewhat agree",
    6: "Agree",
    7: "Strongly agree"
}

mapping_share = {
    1: "Extremely unlikely",
    2: "Moderately unlikely",
    3: "Slightly unlikely",
    4: "Neither likely nor unlikely",
    5: "Slightly likely",
    6: "Moderately likely",
    7: "Extremely likely"
}

# File explorer (as before)
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

# Plot boxplot (as before)
def plot_custom_boxplot(data, block):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    meanprops = dict(color='red', linewidth=1, linestyle='-')
    boxplot = data.boxplot(ax=ax1, patch_artist=True, return_type='dict', showmeans=True, meanline=True, meanprops=meanprops)

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

    ax1.set_title(f'Boxplot of Question Block for {block}', fontsize=13)
    
    x_labels = [f'__real?', f'__credible?', f'__deepfake?', f'__sharing intention']
    ax1.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=12)
    
    for tick in ax1.get_xticklabels():
        if 'sharing intention' in tick.get_text():
            tick.set_color('darkblue')

    # Settings left y-axis labels 
    ax1.set_yticks(range(1, 8))
    ax1.set_yticklabels([f'{mapping_questions[i]}: {i}' for i in range(1, 8)], color='black', fontsize=12)

    # Settings right y-axis labels
    ax2 = ax1.twinx()
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_yticks(range(1, 8))
    ax2.set_yticklabels([f'{i}: {mapping_share[i]}' for i in range(1, 8)], color='darkblue', fontsize=12)

    # Custom plot options
    ax1.axvline(x=3.5, color='darkblue', linestyle='--')
    ax1.grid(True, axis='y')
    ax1.grid(False, axis='x')

    # legend
    handles = [
        plt.Line2D([0], [0], color='orange', linewidth=2, label='Median'),
        plt.Line2D([0], [0], color='red', linewidth=2, label='Mean'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=8, label='Outliers')
    ]
    ax1.legend(handles=handles, loc='upper left')

    plt.tight_layout()
    plt.show()

def main():
    file_path = select_file()
    if file_path is None:
        exit()

    df = pd.read_csv(file_path, skiprows=[1, 2])
    df_filtered = df[df['Finished'] == 1]

    # Question blocks
    block_bases = [
        'Biden_1X1', 'Biden_1X2', 'Biden_1X3', 'Biden_1X4', 'Biden_1X5', 'Biden_3X1', 'Biden_3X2', 'Biden_3X3', 'Biden_3X4', 'Biden_3X5',
        'Trump_1X1', 'Trump_1X2', 'Trump_1X3', 'Trump_1X4', 'Trump_1X5', 'Trump_3X1', 'Trump_3X2', 'Trump_3X3', 'Trump_3X4', 'Trump_3X5',
        'Trump_Bonus'
    ]
    blocks = {base: [f"{base}__1", f"{base}__2", f"{base}__3", f"{base}_share"] for base in block_bases}

    # First Boxplot: "Trump_Bonus" block for all real videos
    trump_bonus_block = "Trump_Bonus"
    if all(q in df_filtered.columns for q in blocks[trump_bonus_block]):
        block_data = df_filtered[blocks[trump_bonus_block]]
        print(f"\nDescriptive Statistics for {trump_bonus_block} (Numerical Values):")
        print(block_data.describe())
        plot_custom_boxplot(block_data, 'All Real Videos')

    # Second Boxplot: Aggregated deepfake blocks
    deepfake_blocks = [block for block in blocks if block != trump_bonus_block]

    # Initialize dictionaries to hold sums and counts for each question type
    sum_dict = {
        'real': 0,
        'credible': 0,
        'deepfake': 0,
        'sharing intention': 0
    }
    count_dict = {
        'real': 0,
        'credible': 0,
        'deepfake': 0,
        'sharing intention': 0
    }

    # Initialize lists to hold all values for calculating medians
    all_values = {
        'real': [],
        'credible': [],
        'deepfake': [],
        'sharing intention': []
    }

    # Process each deepfake block
    for block in deepfake_blocks:
        if all(q in df_filtered.columns for q in blocks[block]):
            block_data = df_filtered[blocks[block]]

            # Aggregate sums and counts for each question type
            sum_dict['real'] += block_data[blocks[block][0]].sum()
            sum_dict['credible'] += block_data[blocks[block][1]].sum()
            sum_dict['deepfake'] += block_data[blocks[block][2]].sum()
            sum_dict['sharing intention'] += block_data[blocks[block][3]].sum()

            count_dict['real'] += block_data[blocks[block][0]].count()
            count_dict['credible'] += block_data[blocks[block][1]].count()
            count_dict['deepfake'] += block_data[blocks[block][2]].count()
            count_dict['sharing intention'] += block_data[blocks[block][3]].count()

            # Collect all values for calculating medians
            all_values['real'].extend(block_data[blocks[block][0]].dropna().tolist())
            all_values['credible'].extend(block_data[blocks[block][1]].dropna().tolist())
            all_values['deepfake'].extend(block_data[blocks[block][2]].dropna().tolist())
            all_values['sharing intention'].extend(block_data[blocks[block][3]].dropna().tolist())

    # Calculate global means
    global_means = {
        'real': sum_dict['real'] / count_dict['real'] if count_dict['real'] > 0 else np.nan,
        'credible': sum_dict['credible'] / count_dict['credible'] if count_dict['credible'] > 0 else np.nan,
        'deepfake': sum_dict['deepfake'] / count_dict['deepfake'] if count_dict['deepfake'] > 0 else np.nan,
        'sharing intention': sum_dict['sharing intention'] / count_dict['sharing intention'] if count_dict['sharing intention'] > 0 else np.nan
    }

    # Calculate global medians
    global_medians = {
        'real': np.median(all_values['real']) if all_values['real'] else np.nan,
        'credible': np.median(all_values['credible']) if all_values['credible'] else np.nan,
        'deepfake': np.median(all_values['deepfake']) if all_values['deepfake'] else np.nan,
        'sharing intention': np.median(all_values['sharing intention']) if all_values['sharing intention'] else np.nan
    }

    # Create DataFrame for plotting
    aggregated_df = pd.DataFrame([global_means, global_medians]).T
    aggregated_df.columns = ['Mean', 'Median']
    aggregated_df = aggregated_df.T  # Transpose to match the expected format

    # Rename columns appropriately
    aggregated_df.columns = [
        '__real',
        '__credible',
        '__deepfake_belief',
        '__sharing intention'
    ]

    print("\nDescriptive Statistics for aggregated deepfake videos (Numerical Values):")
    print(aggregated_df)

    # Plotting the global means and medians
    plot_custom_boxplot(aggregated_df, 'All Deepfake Videos')

if __name__ == "__main__":
    main()
