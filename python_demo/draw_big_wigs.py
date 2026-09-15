#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import \
    build_position_score_from_resource

grr = build_genomic_resource_repository()


res_to_draw = [build_position_score_from_resource(r).open()
               for r in grr.search_resources(
                        "summary liu2026Multiomics Thyroid c5",
                        resource_type="position_score")]

chrom = "chr1"
beg = 27_100_000
end = 27_200_000

xs = np.arange(beg, end+1)

shareax = None
plt.figure(figsize=(10, 10))
for psi, ps in enumerate(res_to_draw, 1):
    plt.subplot(len(res_to_draw), 1, psi, sharex=shareax)
    if psi == 1:
        shareax = plt.gca()
    ys = list(ps.get_score_in_region(chrom, beg, end))
    print(len(ys))
    plt.plot(xs, ys, label=ps.resource_id)
    plt.legend()
plt.show(block=True)
