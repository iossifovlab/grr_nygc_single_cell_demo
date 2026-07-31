import json
import numpy as np
import matplotlib.pyplot as plt


json_fn = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/zemke2024Epigenetic/ATACfragments/hc98/statistics/histogram_cell.json"

with open(json_fn, 'r', encoding='utf-8') as file:
    hist_data = json.load(file)

data = np.array(list(hist_data["values"].values()))
bins = np.logspace(0, np.log10(data.max()), num=50)

plt.figure(figsize=(10, 6))
plt.hist(data, bins=bins, log=True, edgecolor='black', alpha=0.7, color='skyblue')
plt.xscale('log')
plt.xlabel('Count of fragments per cell (log scale)', fontsize=12)
plt.ylabel('Frequency of count (log scale)', fontsize=12)
plt.title('Log-log Distribution of fragments-per-cell Data', fontsize=14, fontweight='bold')
plt.grid(True, which="both", ls="--", alpha=0.5)

plt.show(block=False)