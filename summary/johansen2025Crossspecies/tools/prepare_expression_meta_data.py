import glob
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter
from pathlib import Path


ivanMetadataDir = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/ivan-buff/allen/metadata"


target_dir = Path(ivanMetadataDir)
all_files = [
    str(file)
    for file in target_dir.rglob("*")
    if file.suffix == ".gz"
]


for ff in all_files:
    parts = ff.split("/")
    fn = parts[-1]
    if parts[-2] == "views":
        directory = parts[-4]
        release = parts[-3]
        is_view = True
    else:
        directory = parts[-3]
        release = parts[-2]
        is_view = False

    fn_parts = fn.split(".")
    assert len(fn_parts) == 3
    assert fn_parts[1] == "csv"
    assert fn_parts[2] == "gz"
    base_fn = fn_parts[0]
    print(fn, directory, release, is_view)

    files = [ff]

    if is_view:
        resource_id = f"summary/johansen2025Crossspecies/expression_meta_data/{directory}/{release}/views/{base_fn}"
    else:
        resource_id = f"summary/johansen2025Crossspecies/expression_meta_data/{directory}/{release}/{base_fn}"
    print(resource_id)

    conf = {
        "type": "data_frame",
        "file": fn,
        "meta": {
            "summary": f"Meta data file for expression subset {directory}",
            "description": dedent("""
                [Johansen et al., Cross-species consensus atlas of the primate basal ganglia, bioRxiv, 2025](https://www.biorxiv.org/content/10.64898/2025.12.15.694496v1)

                Downloaded from: [https://alleninstitute.github.io/abc_atlas_access/descriptions/HMBA-BG_dataset.html](https://alleninstitute.github.io/abc_atlas_access/descriptions/HMBA-BG_dataset.html).
            """),
            "labels": {
                "assay": "scRNASeq",
                "directory": directory,
                "release_date": release,
                "technology": "10x genomics",
                "dataset": "johansen2025Crossspecies"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
