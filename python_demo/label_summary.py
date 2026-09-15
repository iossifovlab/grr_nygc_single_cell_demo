#!/usr/bin/env python
'''Print summary of the labels in the NYGC single cell GRR.'''

import sys
from collections import defaultdict
from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository

study = None
if len(sys.argv) > 1:
    study = sys.argv[1]

try:
    grr
except NameError:
    grr = build_genomic_resource_repository()

hists = defaultdict(lambda: defaultdict(lambda: defaultdict(
                                                    lambda: defaultdict(int))))
labels_per_paper = defaultdict(set)
n_objects = defaultdict(int)
resource_types = defaultdict(lambda: defaultdict(int))

res_q = "summary/*" if study is None else f"summary/{study}/*"

for r in grr.search_resources(resource_query=res_q):
    parts = r.resource_id.split("/")
    assert parts[0] == "summary"
    dataset = parts[1]
    subdir = parts[2]

    n_objects[dataset, subdir] += 1
    resource_types[dataset, subdir][r.get_type()] += 1
    for label, value in r.get_labels().items():
        value_s = str(value)
        hists[dataset][subdir][label][value_s] += 1
        labels_per_paper[dataset].add(label)

for dsi, ds_d in hists.items():
    print('=========', dsi, '=========')
    sbdirs = [sbdir for dsi_a, sbdir in n_objects if dsi_a == dsi]
    for sbdir in sbdirs:
        print(f"    ------ {sbdir} [{n_objects[dsi, sbdir]}] ------")

        print("      Resource_types:")
        assert len(resource_types[dsi, sbdir]) == 1
        for rt, rtc in resource_types[dsi, sbdir].items():
            print(f"        {rt} [{rtc}]")

        print("      Labels:")
        if sbdir not in ds_d:
            continue
        sb_d = ds_d[sbdir]
        for lbl in sorted(labels_per_paper[dsi]):
            if lbl not in sb_d:
                continue
            print(f"        {lbl}: ", end="")

            cc = sorted(sb_d[lbl].items(), key=lambda x: (-x[1], [0]))
            other_s = ""
            if len(cc) > 5:
                other_s = f", and {len(cc)-5} others for " + \
                          f"{sum(v for _, v in cc[5:])} resources"
                cc = cc[:5]
            print("; ".join([f"{lb} [{v}]" for lb, v in cc]), other_s, sep="")
            ys = list(sb_d[lbl].values())
