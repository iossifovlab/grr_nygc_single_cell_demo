#!/usr/bin/env python

import pathlib
import pandas as pd
from typing import cast
import matplotlib.pyplot as plt
import numpy as np

from gain.genomic_resources.repository_factory import build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import build_position_score_from_resource
from gain.genomic_resources.genomic_scores import PositionScore

grr = build_genomic_resource_repository()


# res_to_draw: list[PositionScore] = []
# for r in grr.get_all_resources():
#     if r.get_type() != "position_score":
#         continue
#     if not r.get_id().startswith("summary/liu2026Multiomics/bigwig/Thyroid/c5"):
#         continue
#     score = build_position_score_from_resource(r).open()
#     res_to_draw.append(score)

res_to_draw = [build_position_score_from_resource(r).open()
               for r in grr.search_resources(
                        "summary liu2026Multiomics bigwig Thyroid c5",
                        resource_type="position_score")]

chrom = "chr1"
beg = 27_100_000
end = 27_200_000

xs = np.arange(beg, end+1)

yss = []
shareax = None
plt.figure(figsize=(10, 10))
for psi, ps in enumerate(res_to_draw, 1):
    plt.subplot(3, 1, psi, sharex=shareax)
    if psi == 1:
        shareax = plt.gca()
    scr_name = ps.get_all_scores()[0]
    ys = ps.get_region_scores(chrom, beg, end, scr_name)
    yss.append(ys)
    print(len(ys))
    plt.plot(xs, ys, label=scr_name)
    plt.legend()
plt.show(block=True)


