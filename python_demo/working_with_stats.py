from collections import defaultdict
import matplotlib.pyplot as plt

import gain.grr as grr
from gain.genomic_resources.histogram import NumberHistogram

GRR = grr.build_genomic_resource_repository()

mns = defaultdict(list)
for r in GRR.search_resources("data_types : atac_signal",
                              resource_type="position_score"):
    sc = grr.build_position_score_from_resource(r)

    hist = sc.get_score_histogram()

    assert isinstance(hist, NumberHistogram)
    mn = hist.mean

    study, study_componeent = r.resource_id.split("/")[1:3]
    mns[(study, study_componeent)].append(mn)

plt.figure(figsize=(6, 6))
for si, ((study, component), vs) in enumerate(mns.items(), 1):
    plt.subplot(len(mns), 1, si)
    plt.plot(sorted(vs))
    plt.title(f"{study}/{component}")
plt.tight_layout()
plt.show()
