from collections import defaultdict, Counter

import gain.grr as grr

GRR = grr.build_genomic_resource_repository()

hists = defaultdict(lambda : Counter())
for r in GRR.get_all_resources():
    for l, v in r.get_labels().items():
        hists[l][str(v)] += 1
print(hists)
