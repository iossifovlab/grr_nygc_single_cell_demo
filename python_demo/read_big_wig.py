#!/usr/bin/env python

from gain.genomic_resources.repository_factory import build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import build_position_score_from_resource
import pyBigWig
from urllib.parse import urlparse
from urllib.request import url2pathname
import numpy as np
from collections import defaultdict
from typing import cast

from gain.utils.verbosity_configuration import VerbosityConfiguration
from gain import logging
VerbosityConfiguration.adjust_verbosity(logging.DEBUG)

from gain.genomic_resources.genomic_scores import build_score_from_resource
from gain.genomic_resources.genomic_scores import PositionScore


try:
    grr
except NameError:
    grr = build_genomic_resource_repository()


resources = [
#     grr.get_resource("summary/zemke2023Conserved/pseudo_bulk_mc_bedgraph/Human/CLA/CGN")
]
for res in grr.search_resources("liu2026Multiomics Thyroid c5", 
                                resource_type="position_score"):
    resources.append(res)

for res in resources:
    print(f"working with {res.resource_id}")
    print("The file url is:", res.get_file_url(res.config["table"]["filename"]))

    # #
    # # do that with bigwig's native interface 
    # #
    bw = res.open_bigwig_file(res.config["table"]["filename"])
    interval_length_hist = defaultdict(int)
    mn = np.inf
    mx = -np.inf
  
    chrom_sizes = bw.chroms()
    for chr_i, (chrom, length) in enumerate(chrom_sizes.items()):
        intervals = bw.intervals(chrom, 0, length)
        print(chrom, len(intervals))
        if intervals:
            for iii, (start, end, value) in enumerate(intervals):
                if (iii % 100_000) == 0:
                    print(iii, (start, end, value))
                # Process your data here (e.g., write to a file or analyze)
                # print(f"{chrom}:{start}-{end} = {value}")
                mn = min(mn, value)
                mx = max(mx, value)
                interval_length_hist[end-start] += 1
        break
    print("Result", res, mn, mx, interval_length_hist)

    #
    # do that with bigwig's directly
    #
    score = build_position_score_from_resource(res).open()
    interval_length_hist = defaultdict(int)
    mn = np.inf
    mx = -np.inf
    assert len(score.get_all_scores()) == 1

    for chr_i, chrom in enumerate(score.get_all_chromosomes()):
        for iii, (start, end, values) in enumerate(score.fetch_region_values(chrom, 1, 300_000_000)):
            if (iii % 100_000) == 0:
                print(iii, (start, end, values))
            # print(start, end, values)
            if values is not None:
                assert len(values) == 1
                value = values[0]
                mn = min(mn, value)
                mx = max(mx, value)
                interval_length_hist[end-start] += 1
        # if chr_i > 3:
        break
    print("Result", res, mn, mx, interval_length_hist)


