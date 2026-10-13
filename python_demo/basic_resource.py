import gain.grr as grr


repo = grr.build_genomic_resource_repository()
for r in repo.search_resources("cell_type : Astro"):
    print(r.resource_id, r.get_type(), r.get_labels())

score_id = "summary/zemke2023Conserved/pseudobulk_atac/human_m1/ASC"
score = grr.build_position_score_from_resource_id(score_id).open()
ys = list(score.get_score_in_region("chr1", 151_403_000, 151_403_100))
print(ys)
