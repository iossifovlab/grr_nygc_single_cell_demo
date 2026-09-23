# Working with GRR
from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository

grr = build_genomic_resource_repository()
for r in grr.search_resources("cell_type : Astro"):
    print(r.resource_id, r.get_type(), r.get_labels())


# Working with a PositionScore
from gain.genomic_resources.genomic_scores import \
    build_position_score_from_resource_id

score_id = "summary/zemke2023Conserved/pseudobulk_atac/human_m1/ASC"
score = build_position_score_from_resource_id(score_id).open()
ys = list(score.get_score_in_region("chr1", 151_403_000, 151_403_100))
print(ys)
