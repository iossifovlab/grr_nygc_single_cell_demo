import pathlib
import pandas as pd
from typing import cast

from gain.genomic_resources.repository_factory import build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import build_score_from_resource_id
from gain.genomic_resources.genomic_scores import PositionScore



grr = build_genomic_resource_repository()


## Find all resources for a cell-type
for r in grr.get_all_resources():
    if r.get_labels().get("cell_type") == "Astro":
        print(r.resource_id)

## Using basic resource
basic_resource_id = "summary/zemke2023Conserved/cell_expression/by_sample/M1_Peregrine_rep1"
basic_resource = grr.get_resource(basic_resource_id)
features = pd.read_csv(basic_resource.get_file_url("M1_Peregrine_rep1_features.tsv.gz"), sep="\t")
print(features)


## Using basic resource
score_id = "summary/zemke2023Conserved/pseudo_bulk_atac_bw/human_m1/ASC"
score = cast(PositionScore, build_score_from_resource_id(score_id).open())

xs = []
ys = []
for pos_begin, pos_end, values in score.fetch_region("chr1", 151_402_724, 151_459_494):
    if values is not None:
        xs += range(pos_begin, pos_end + 1)
        ys += [values[0]]*(pos_end - pos_begin + 1)


