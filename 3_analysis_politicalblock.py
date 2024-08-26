import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import filedialog


# File explorer
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

file_path = select_file()
if file_path is None:
    print("No file selected.")
    exit()

# Load the recoded CSV file, skip descriptor and JSON rows 
df = pd.read_csv(file_path, skiprows=[1, 2])

# Only take valid answers into account
df_filtered = df[df['Finished'] == 1]

# Test for correct filtering
print(df['Finished'].unique())
# print("First few rows:")
# print(df_filtered.head())

pre_influence_cols = {
    "health": "stance_health",
    "climate": "stance_climate",
    "immigration": "stance_immigration",
    "guns": "stance_guns",
    "abortion": "stance_abortion",
    "warukr": "stance_warukr"
}

post_influence_cols = {
    "health": "2stance_health",
    "climate": "2stance_climate",
    "immigration": "2stance_immigration",
    "guns": "2stance_guns",
    "abortion": "2stance_abortion",
    "warukr": "2stance_warukr"
}

stance_titles = {
    "health": "healthcare policy",
    "climate": "climate-change mitigation policy",
    "immigration": "immigration policy",
    "guns": "gun control policy",
    "abortion": "abortion policy",
    "warukr": "ukraine war policy"
}

t_test_results = {}

# paired t-test for each pair of pre and post influence question
for key, pre_col in pre_influence_cols.items():
    post_col = post_influence_cols[key]
    
    # Drop rows with missing values if needed
    paired_data = df_filtered[[pre_col, post_col]].dropna()
    
    # Check if data is correctly filtered
    if paired_data.empty:
        print(f"No data available for {pre_col} and {post_col}. Skipping...")
        continue

    # data to float
    pre_data = paired_data[pre_col].astype(float)
    post_data = paired_data[post_col].astype(float)
    
    # paired t-test
    t_stat, p_val = stats.ttest_rel(post_data, pre_data)
    t_test_results[key] = (t_stat, p_val)
    significance = "Significant difference" if p_val < 0.05 else "No significant difference"
    
    descriptions = {
        "healthcare policy": [
            "Completely publicly funded", 
            "Moderately publicly funded", 
            "Somewhat publicly funded", 
            "Neutral", 
            "Somewhat privatized", 
            "Moderately privatized", 
            "Completely privatized"
        ],
        "climate-change mitigation policy": [
            "Completely in favor", 
            "Moderately in favor", 
            "Somewhat in favor", 
            "Neutral", 
            "Somewhat against", 
            "Moderately against", 
            "Completely against"
        ],
        "immigration policy": [
            "Completely open borders, [...]", 
            "Moderately open borders [...]", 
            "Somewhat open borders [...]", 
            "Neutral", 
            "Somewhat strict [...]", 
            "Moderately strict [...]", 
            "Completely closing borders [...]"
        ],
        "gun control policy": [
            "Everybody is allowed [...]", 
            "Widespread ownership, [...]", 
            "Controlled ownership [...]", 
            "Neutral", 
            "Significant restrictions, [...]", 
            "Highly restricted, [...]", 
            "No one is allowed [...]"
        ],
        "abortion policy": [
            "Unrestricted access [...]", 
            "Few restrictions, [...]", 
            "Moderate restrictions, [...]", 
            "Neutral", 
            "Restricted access, [...]", 
            "Very restricted access, [...]", 
            "Complete ban on abortion"
        ],
        "ukraine war policy": [
            "Fully support [...] intervention, [...]", 
            "Support intervention [...] significant aid [...]", 
            "Support intervention [...] some [aid]", 
            "Neutral", 
            "Oppose intervention, [...]", 
            "Strongly oppose intervention, [...]", 
            "Completely oppose [intervention]"
        ]
    }
    
    # Groupplot
    # gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    default_hist_color = 'lightblue'
    pre_color = 'turquoise'
    post_color = 'darkblue'

    # Histogram
    # plt.subplot(gs[0])
    plt.figure(figsize=(8, 9))
    plt.hist(pre_data, bins=7, range=(1, 7), alpha=0.5, color=default_hist_color)
    plt.hist(post_data, bins=7, range=(1, 7), alpha=0.5, color=default_hist_color)
    plt.hist(pre_data, bins=7, range=(1, 7), alpha=0.5, color=pre_color, label='Pre')
    plt.hist(post_data, bins=7, range=(1, 7), alpha=0.5, color=post_color, label='Post')
    plt.axvline(4, color='r', linestyle='dashed', linewidth=1)  # Add vertical neutral line
    plt.xlabel(' ')
    plt.ylabel('Frequency')
    plt.xticks(range(1, 8), descriptions[stance_titles[key]], rotation=45, ha='right')
    plt.title(f'Histogram of {stance_titles[key]}')
    plt.legend()
    plt.subplots_adjust(left=0.2, bottom=0.3)
    plt.show()

    # Boxplot
    # plt.subplot(gs[1])
    plt.figure(figsize=(9, 8))
    plt.boxplot([post_data, pre_data], vert=False, labels=['Post', 'Pre'])
    plt.axvline(4, color='r', linestyle='dashed', linewidth=1)  # Add vertical neutral line
    plt.xlabel(' ')
    plt.xticks(range(1, 8), descriptions[stance_titles[key]], rotation=45, ha='right')
    plt.title(f'Boxplot of {stance_titles[key]}')
    plt.subplots_adjust(left=0.2, bottom=0.3)
    plt.show()

    # plt.figtext(0.5, 0.01, f'T-test results for {stance_titles[key]}: t-statistic = {t_stat:.2f}, p-value = {p_val:.4f}\n{significance}', ha='center', fontsize=12, bbox={"facecolor":"white", "alpha":0.75, "pad":5})
    # plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    # plt.show()
       
# Display t-test results
for key, (t_stat, p_val) in t_test_results.items():
    significance = "Significant difference" if p_val < 0.05 else "No significant difference"
    print(f"T-test for {stance_titles[key]}: t-statistic={t_stat:.2f}, p-value={p_val:.4f}")
    print(f"{significance} in {stance_titles[key]} before and after the video.")