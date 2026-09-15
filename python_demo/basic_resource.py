import pandas as pd
import numpy as np

from gain.genomic_resources.repository_factory import build_genomic_resource_repository
from gain.genomic_resources.genomic_scores import build_position_score_from_resource_id


grr = build_genomic_resource_repository()


# # Find all resources for a cell-type
# for r in grr.get_all_resources():
#     if r.get_labels().get("cell_type") == "Astro":
#         print(r.resource_id)

for r in grr.search_resources("cell_type : Astro"):
    print(r.resource_id)


# Using basic resource
basic_resource_id = "summary/zemke2023Conserved/rna_expression_atac_matrix/M1_Peregrine_rep1"
basic_resource = grr.get_resource(basic_resource_id)
features = pd.read_csv(basic_resource.get_file_url("M1_Peregrine_rep1_features.tsv.gz"), sep="\t")
print(features)


# Using position score
score_id = "summary/zemke2023Conserved/pseudobulk_atac/human_m1/ASC"
score = build_position_score_from_resource_id(score_id).open()


ys = np.array(list(score.get_score_in_region("chr1", 151_402_724, 151_459_494)))
print(ys)
