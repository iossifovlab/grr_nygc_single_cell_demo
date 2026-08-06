from gain.genomic_resources.repository_factory import build_genomic_resource_repository
from collections import defaultdict
import matplotlib.pylab as plt

try:
    grr
except NameError:
    grr = build_genomic_resource_repository()

hists = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
labels_per_paper = defaultdict(set)
n_objects = defaultdict(int)
resource_types = defaultdict(lambda: defaultdict(int))

for r in grr.get_all_resources():
    if not r.resource_id.startswith("summary"):
        continue

    parts = r.resource_id.split("/")
    assert parts[0] == "summary"
    dataset = parts[1]
    subdir = parts[2]

    n_objects[dataset, subdir] += 1
    resource_types[dataset, subdir][r.get_type()] += 1
    for label, value in r.get_labels().items():
        hists[dataset][subdir][label][value] += 1
        labels_per_paper[dataset].add(label)

for dsi, ds_d in hists.items():
    print(dsi)
    sbdirs = [sbdir for dsi_a, sbdir in n_objects if dsi_a == dsi]
    for sbdir in sbdirs:
        print(f"    {sbdir} [{n_objects[dsi, sbdir]}]")

        print("      Resource_types:")
        assert len(resource_types[dsi, sbdir]) == 1
        for rt, rtc in resource_types[dsi, sbdir].items():
            print(f"        {rt} [{rtc}]")

        print("      Labels:")
        if sbdir not in ds_d:
            continue
        sb_d = ds_d[sbdir]
        for lbl in labels_per_paper[dsi]:
            if lbl not in sb_d:
                continue
            print(f"        {lbl}: ", end="")

            cc = sorted(sb_d[lbl].items(), key=lambda x: (-x[1], [0]))
            other_s = ""
            if len(cc) > 5:
                other_s = f", and {len(cc)-5} others for {sum(v for _, v in cc[5:])} resources"
                cc = cc[:5]
            print("; ".join([f"{l} [{v}]" for l, v in cc]), other_s, sep="")
            xlbls = list(sb_d[lbl].keys())
            ys = list(sb_d[lbl].values())




# for dsi, ds_d in hists.items():
#     plt.figure(figsize=(20, 20))
#     spi = 0
#     for sbdi, (sbdir, sb_d) in enumerate(ds_d.items()):
#         for lbli, lbl in enumerate(labels_per_paper[dsi]):
#             spi += 1
#             plt.subplot(len(ds_d), len(labels_per_paper[dsi]), spi)
#             # if sbdi == 0:
#             #     plt.title(f"{lbl}")
#             if lbli == 0:
#                 plt.ylabel(f"{sbdir}\n{n_objects[dsi, sbdir]}")
#             if lbl not in sb_d:
#                 continue
#             xlbls = list(sb_d[lbl].keys())
#             ys = list(sb_d[lbl].values())
#             plt.plot(ys, '*')
#             plt.xticks(range(len(ys)), labels=xlbls)
#             plt.xlabel(lbl)
#     plt.suptitle(dsi)
#     plt.tight_layout()
# plt.show(block=False)


