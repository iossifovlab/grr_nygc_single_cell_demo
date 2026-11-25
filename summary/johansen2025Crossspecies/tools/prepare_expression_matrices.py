
import io
import pandas as pd
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter
from pathlib import Path


ivanMetadataDir = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/ivan-buff/allen/expression_matrices"


labels_raw="""base_name	technology	assay	species	measure
HMBA-10xMultiome-BG-Aligned-log2	10x-Genomics	scRNA	human,macaque,marmoset	log2
HMBA-10xMultiome-BG-Aligned-raw	10x-Genomics	scRNA	human,macaque,marmoset	raw
HMBA-10xMultiome-BG-Human-log2	10x-Genomics	scRNA	human	log2
HMBA-10xMultiome-BG-Human-raw	10x-Genomics	scRNA	human	raw
HMBA-10xMultiome-BG-Macaque-log2	10x-Genomics	scRNA	macaque	log2
HMBA-10xMultiome-BG-Macaque-raw	10x-Genomics	scRNA	macaque	raw
HMBA-10xMultiome-BG-Marmoset-log2	10x-Genomics	scRNA	marmoset	log2
HMBA-10xMultiome-BG-Marmoset-raw	10x-Genomics	scRNA	marmoset	raw
MERSCOPE-H22.30.001-BG-log2	spatial-MERSCOPE	scRNA	human	log2
MERSCOPE-H22.30.001-BG-raw	spatial-MERSCOPE	scRNA	human	raw
MERSCOPE-QM23.50.001-BG-log2	spatial-MERSCOPE	scRNA	macaque	log2
MERSCOPE-QM23.50.001-BG-raw	spatial-MERSCOPE	scRNA	macaque	raw
HMBA-Macaque-PatchSeq-BG-log2	PatchSeq	scRNA	macaque	log2
Xenium-CJ23.56.004-BG-log2	spatial-Xenium	scRNA	marmoset	log2
Xenium-CJ23.56.004-BG-raw	spatial-Xenium	scRNA	marmoset	raw
"""

labels_df = pd.read_csv(io.StringIO(labels_raw), sep="\t")
labels_df.set_index("base_name", inplace=True)


def species_label(value):
    if "," in value:
        return value.split(",")
    return value


target_dir = Path(ivanMetadataDir)
all_files = [
    str(file)
    for file in target_dir.rglob("*")
    if file.suffix == ".h5ad"
]


for ff in sorted(all_files):
    parts = ff.split("/")
    fn = parts[-1]
    release = parts[-2]
    directory = parts[-3]

    base_fn = fn[:-5]
    # print(base_fn, fn, directory, release, base_fn)
    print(base_fn)

    assert base_fn in labels_df.index
    files = [ff]

    resource_id = f"summary/johansen2025Crossspecies/expression_matrix/{directory}/{release}/{base_fn}"
    print(resource_id)

    conf = {
        "type": "ann_data",
        "file": fn,
        "meta": {
            "summary": f"Expression matrix {base_fn}",
            "description": dedent("""
                [Johansen et al., Cross-species consensus atlas of the primate basal ganglia, bioRxiv, 2025](https://www.biorxiv.org/content/10.64898/2025.12.15.694496v1)

                Downloaded from: [https://alleninstitute.github.io/abc_atlas_access/descriptions/HMBA-BG_dataset.html](https://alleninstitute.github.io/abc_atlas_access/descriptions/HMBA-BG_dataset.html).
            """),
            "labels": {
                "assay": "scRNASeq",
                "directory": directory,
                "release_date": release,
                "technology": labels_df.at[base_fn, 'technology'],
                "species": species_label(labels_df.at[base_fn, 'species']),
                "measure": labels_df.at[base_fn, 'measure'],
                "dataset": "johansen2025Crossspecies"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
