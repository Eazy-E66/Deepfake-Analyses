import json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import tkinter as tk
from tkinter import filedialog

def select_file(prompt_message):
    print(prompt_message)
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        print("No file selected.")
        return None
    return file_path

file_path_credible = select_file("Select credible JSON file")
if file_path_credible is None:
    exit()

with open(file_path_credible, 'r') as f:
    data_credible = json.load(f)

file_path_share = select_file("Select share JSON file")
if file_path_share is None:
    exit()

with open(file_path_share, 'r') as f:
    data_share = json.load(f)

x_data = []
y_data = []

for key in data_credible.keys():
    share_key = key.replace('__2', '_share')

    credible_scores = data_credible[key]
    share_scores = data_share.get(share_key)

    if share_scores is not None:
        x_data.extend(credible_scores)
        y_data.extend(share_scores)

x_data_np = np.array(x_data).reshape(-1, 1)
y_data_np = np.array(y_data)

if len(x_data_np) == 0 or len(y_data_np) == 0:
    print("No match")
    exit()

plt.scatter(x_data, y_data, color='lightblue', alpha=0.5, label='Data points')

model = LinearRegression()
model.fit(x_data_np, y_data_np)
y_pred = model.predict(x_data_np)

plt.plot(x_data, y_pred, color='orange', label='Overall regression line')

plt.xlabel('Credibility Ratings', fontsize=14, fontstyle='italic')
plt.ylabel('Sharing Intention', fontsize=14, fontstyle='italic')
plt.title('Overall Trend', fontsize=16)
plt.xlim(1, 7)
plt.ylim(1, 7)
plt.xticks(np.arange(1, 8, 1), fontsize=12)
plt.yticks(np.arange(1, 8, 1), fontsize=12)
plt.legend(fontsize=14)
plt.grid(True)
plt.show()
