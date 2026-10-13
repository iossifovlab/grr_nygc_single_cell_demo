import matplotlib.pyplot as plt

from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import \
    build_position_score_from_resource
from gain.genomic_resources.histogram import NumberHistogram

grr = build_genomic_resource_repository()

mns = []
for r in grr.search_resources("data_types : atac_signal",
                              resource_type="position_score"):
    sc = build_position_score_from_resource(r)
    scores = sc.get_all_scores()
    assert len(scores) == 1
    score = scores[0]

    hist = sc.get_score_histogram(score)
    assert isinstance(hist, NumberHistogram)
    mn = hist.mean
    print(r.resource_id, score, mn)   # , r.get_labels())
    mns.append(mn)

plt.figure()
plt.plot(mns)
plt.show(block=False)
