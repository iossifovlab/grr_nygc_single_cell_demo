import numpy as np
from typing import IO
from gain.genomic_resources.histogram import CategoricalHistogram
import matplotlib.pyplot as plt


def plot_fragment_per_cell_count(outfile: IO, histogram: CategoricalHistogram, xlabel: str, *_args, **_kw) -> None:
    data = np.array(list(histogram.raw_values.values()))

    bins = np.logspace(0, np.log10(data.max()), num=50)

    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=bins, log=True, edgecolor='black', alpha=0.7, color='skyblue')
    plt.xscale('log')
    plt.xlabel('Count of fragments per cell (log scale)', fontsize=12)
    plt.ylabel('Frequency of count (log scale)', fontsize=12)
    plt.title(f'Log-log Distribution of fragments-per-cell Data {len(data)} cells', fontsize=14, fontweight='bold')
    plt.grid(True, which="both", ls="--", alpha=0.5)

    plt.savefig(outfile); plt.clf()

