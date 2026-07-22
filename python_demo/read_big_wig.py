from gain.genomic_resources.repository_factory import build_genomic_resource_repository
import pyBigWig
from urllib.parse import urlparse
from urllib.request import url2pathname
import numpy as np
from collections import defaultdict

try:
    grr
except NameError:
    grr = build_genomic_resource_repository()

# res = grr.get_resource("summary/zemke2023Conserved/pseudo_bulk_atac_bw/human_m1/L4_5_IT")


for res in grr.search_resources("liu2026Multiomics Thyroid c6 obs_pval_signal", resource_type="position_score"):
    interval_lenght_hist = defaultdict(int)

    print("Working with", res.resource_id)
    file_url = res.get_file_url(res.config["table"]["filename"])
    if file_url.startswith("file"):
        bw = pyBigWig.open(url2pathname(urlparse(file_url).path))
    else:
        bw = pyBigWig.open(file_url)

    chrom_sizes = bw.chroms()

    mn = np.inf
    mx = -np.inf
    for chrom, length in chrom_sizes.items():
        intervals = bw.intervals(chrom, 0, length)
        print(chrom, len(intervals))
        if intervals:
            for start, end, value in intervals:
                # Process your data here (e.g., write to a file or analyze)
                print(f"{chrom}:{start}-{end} = {value}")
                mn = min(mn, value)
                mx = max(mx, value)
                interval_lenght_hist[end-start] += 1

    bw.close()
    print("Result", res, mn, mx, interval_lenght_hist)
