#!/usr/bin/env python

import time
from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import \
    build_position_score_from_resource
import numpy as np
from collections import defaultdict

from gain.utils.verbosity_configuration import VerbosityConfiguration
from gain import logging
VerbosityConfiguration.adjust_verbosity(logging.DEBUG)


grr = build_genomic_resource_repository()


resources = list(grr.search_resources("liu2026Multiomics Thyroid c5",
                                      resource_type="position_score"))

for res in resources:
    print(res.resource_id)
    # # #
    # # # do that with bigwig's native interface 
    # # #
    print("Native bw interface...")
    t_start = time.time()
    bw = res.open_bigwig_file(res.config["table"]["filename"])
    interval_length_hist = defaultdict(int)
    mn = np.inf
    mx = -np.inf

    chrom_sizes = bw.chroms()
    for chr_i, (chrom, length) in enumerate(chrom_sizes.items()):
        intervals = bw.intervals(chrom, 0, length)
        print("\t", chrom, len(intervals))
        if intervals:
            for iii, (start, end, value) in enumerate(intervals):
                if (iii % 1_000_000) == 0:
                    print("\t\t", iii, (start, end, value))
                mn = min(mn, value)
                mx = max(mx, value)
                # interval_length_hist[end-start] += 1
        break
    t_end = time.time()
    print(f"\tResult in {t_end-t_start:.1f} seconds", mn, mx) # , interval_length_hist)


    #
    # do that gains generator interface
    #
    print("GAIn generator interface")
    t_start = time.time()
    score = build_position_score_from_resource(res).open()
    interval_length_hist = defaultdict(int)
    mn = np.inf
    mx = -np.inf
    assert len(score.get_all_scores()) == 1

    for chr_i, chrom in enumerate(score.get_all_chromosomes()):
        print("\t", chrom)

        for iii, (start, end, values) in \
                enumerate(score.fetch_region_segments_scores(chrom)):
            if (iii % 1_000_000) == 0:
                print("\t\t", iii, (start, end, values))
            assert values is not None and len(values) == 1
            value = values[0]
            mn = min(mn, value)
            mx = max(mx, value)
            # interval_length_hist[end-start] += 1
        break
    score.close()
    t_end = time.time()
    print("\t", f"Result in {t_end-t_start:.1f} seconds", mn, mx) # , interval_length_hist)

    #
    # do that gains array interface
    #
    print("GAIn array interface")
    t_start = time.time()
    score = build_position_score_from_resource(res).open()
    interval_length_hist = defaultdict(int)
    mn = np.inf
    mx = -np.inf
    assert len(score.get_all_scores()) == 1

    scr_name = score.get_all_scores()[0]
    for chr_i, chrom in enumerate(score.get_all_chromosomes()):
        print("\t", chrom)
        for iii, (starts, ends, values_dict) in \
                enumerate(score.fetch_region_value_arrays(
                    chrom, None, None, [scr_name])):
            if (iii % 100) == 0:
                print("\t\t", iii, f"batch_size: {len(starts)}...")
            values = values_dict[scr_name]
            mn = min(mn, values.min())
            mx = max(mx, values.max())
            # for ln in ends-starts:
            #     interval_length_hist[ln] += 1
        break
    score.close()
    t_end = time.time()
    print(f"\tResult in {t_end-t_start:.1f} seconds", mn, mx) # , interval_length_hist)


