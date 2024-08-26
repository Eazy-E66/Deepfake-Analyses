import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Mappings
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

# File explorer
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

# Map numerical values to descriptions
def map_values(value, mapping):
    lower = int(np.floor(value))
    upper = int(np.ceil(value))
    if lower == upper:
        return mapping[lower]
    return f"{mapping[lower]} - {mapping[upper]}"

# Plot boxplot
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

    ax1.set_title(f'Boxplot of Question Block for {block}')
    
    x_labels = [f'{block}__real?', f'{block}__credible?', f'{block}__deepfake?', f'{block}__sharing intention']
    ax1.set_xticklabels(x_labels, rotation=45, ha='right')
    
    for tick in ax1.get_xticklabels():
        if 'sharing intention' in tick.get_text():
            tick.set_color('darkblue')

    # Settings left y-axis labels 
    ax1.set_yticks(range(1, 8))
    ax1.set_yticklabels([f'{mapping_questions[i]}: {i}' for i in range(1, 8)], color='black')

    # Settings right y-axis labels
    ax2 = ax1.twinx()
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_yticks(range(1, 8))
    ax2.set_yticklabels([f'{i}: {mapping_share[i]}' for i in range(1, 8)], color='darkblue')

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

    for block, questions in blocks.items():
        if all(q in df_filtered.columns for q in questions):
            block_data = df_filtered[questions]

            block_data_described = block_data.describe().loc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
            
            # Column descriptors using mappings
            column_descriptors = []
            for q in questions:
                if q.endswith('__1'):
                    column_descriptors.append(f"{block} real")
                elif q.endswith('__2'):
                    column_descriptors.append(f"{block} credible")
                elif q.endswith('__3'):
                    column_descriptors.append(f"{block} deepfake_belief")
                elif q.endswith('_share'):
                    column_descriptors.append(f"{block} sharing intention")
            
            block_data_described.columns = column_descriptors
            
            mean_txt = pd.DataFrame([map_values(val, mapping_questions if 'sharing intention' not in col else mapping_share) for val, col in zip(block_data_described.loc['mean'], block_data_described.columns)], index=block_data_described.columns, columns=['mean_txt']).T
            
            print(f"\nDescriptive Statistics for {block} (Numerical Values):")
            print(block_data_described)
            
            plot_custom_boxplot(block_data, block)

if __name__ == "__main__":
    main()
