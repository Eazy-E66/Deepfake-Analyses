import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
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

def load_and_filter_data(file_path):
    df = pd.read_csv(file_path, skiprows=[1, 2])
    df_filtered = df[df['Finished'] == 1]
    return df_filtered

def paired_t_test(pre_data, post_data):
    return stats.ttest_rel(post_data, pre_data)

def plot_data(pre_data, post_data, title, descriptions, use_custom_box=False):
    subplot_size = 4
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(2*subplot_size + 2, subplot_size + 2))

    # Histogram
    axes[0].hist(pre_data, bins=7, range=(1, 7), alpha=0.4, color='turquoise', label='Pre')
    axes[0].hist(post_data, bins=7, range=(1, 7), alpha=0.4, color='darkblue', label='Post')
    axes[0].axvline(4, color='r', linestyle='dashed', linewidth=1)
    axes[0].set_title('Histogram', fontsize=15)
    axes[0].set_xticks(range(1, 8))
    axes[0].set_xticklabels(range(1, 8), fontsize=12)
    axes[0].tick_params(axis='y', labelsize=12)
    axes[0].legend()

    # Boxplot
    axes[1].boxplot([post_data, pre_data], vert=False, labels=['Post', 'Pre'])
    axes[1].axvline(4, color='r', linestyle='dashed', linewidth=1)
    axes[1].set_title('Boxplot', fontsize=15)
    axes[1].set_xticks(range(1, 8))
    axes[1].set_xticklabels(range(1, 8), fontsize=12)
    axes[1].tick_params(axis='y', labelsize=15)

    # Adjust layout to minimize margins and leave space for legend box
    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.25)  # Adjust bottom to make space for legend box

    # Create the legend box using the provided parameters
    create_legend_box(fig, descriptions)
    
    plt.suptitle(title, fontsize=18)
    plt.show()

def create_legend_box(fig, descriptions):
    # Fixed box position parameters
    left = 0.05  # Start of the box, relative to figure width
    right = 0.95  # End of the box, relative to figure width
    base_box_height = 0.1  # Base box height relative to figure height
    box_y_position = 0.02  # Y-position for the bottom of the box, relative to figure height

    # Combine the descriptions into a single formatted string
    text = "  ".join([f"{i+1} = {desc}" for i, desc in enumerate(descriptions)])

    # Check the length of the text and decide how many rows are needed
    max_characters_per_line = 90  # Set a threshold for text length
    text_rows = []  # Will hold multiple rows of text

    if len(text) <= max_characters_per_line:
        text_rows = [text]  # Single row
        box_height = base_box_height  # Standard box height for one row
    else:
        # Split into multiple rows
        third_row_needed = len(text) > max_characters_per_line * 2
        if third_row_needed:
            third_len = len(descriptions) // 3
            text_rows = [
                "  ".join([f"{i+1} = {desc}" for i, desc in enumerate(descriptions[:third_len])]),
                "  ".join([f"{i+1} = {desc}" for i, desc in enumerate(descriptions[third_len:2*third_len], start=third_len)]),
                "  ".join([f"{i+1} = {desc}" for i, desc in enumerate(descriptions[2*third_len:], start=2*third_len)])
            ]
            box_height = base_box_height * 1.5  # Increase box height for three rows
        else:
            half_len = len(descriptions) // 2
            text_rows = [
                "  ".join([f"{i+1} = {desc}" for i, desc in enumerate(descriptions[:half_len])]),
                "  ".join([f"{i+1} = {desc}" for i, desc in enumerate(descriptions[half_len:], start=half_len)])
            ]
            box_height = base_box_height * 1.25  # Increase box height for two rows

    # Position and draw the "X-Axis:" label above the box with increased distance
    plt.figtext((left + right) / 2, box_y_position + box_height + 0.03, "X-Axis:", ha="center", va="center", fontsize=15)

    # Add the text inside the legend box, aligned to the top-left
    for i, row in enumerate(text_rows):
        plt.figtext(left + 0.01, box_y_position + box_height - 0.04 * (i + 1), row, ha="left", va="top", fontsize=12)

    # Draw the black outline box at the bottom of the figure with dynamic height
    rect = plt.Rectangle((left, box_y_position), right - left, box_height, linewidth=1.5, edgecolor='black', facecolor='none', transform=fig.transFigure)
    fig.add_artist(rect)

def analyze_stances(df, pre_influence_cols, post_influence_cols, stance_titles, descriptions, use_custom_box=False):
    t_test_results = {}
    for key in pre_influence_cols:
        pre_col = pre_influence_cols[key]
        post_col = post_influence_cols[key]

        paired_data = df[[pre_col, post_col]].dropna()

        pre_data = paired_data[pre_col].astype(float)
        post_data = paired_data[post_col].astype(float)

        t_stat, p_val = paired_t_test(pre_data, post_data)
        t_test_results[key] = (t_stat, p_val)

        significance = "Significant difference" if p_val < 0.05 else "No significant difference"
        print(f"T-test for {stance_titles[key]}: t-statistic={t_stat:.2f}, p-value={p_val:.4f}")
        print(f"{significance} in {stance_titles[key]} before and after the video.")

        plot_data(pre_data, post_data, stance_titles[key], descriptions[stance_titles[key]], use_custom_box)

    return t_test_results

def main():
    file_path = select_file()
    if file_path is None:
        print("No file selected.")
        return

    df_filtered = load_and_filter_data(file_path)

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

    t_test_results = analyze_stances(df_filtered, pre_influence_cols, post_influence_cols, stance_titles, descriptions, use_custom_box=True)

if __name__ == "__main__":
    main()
