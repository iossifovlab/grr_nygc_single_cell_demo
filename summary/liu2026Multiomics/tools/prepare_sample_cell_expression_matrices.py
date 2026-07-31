import glob
import os
import gzip
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce, get_resource_dir

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/HDMA/ATAC_RNA"

for ff in glob.glob(f"{yoonHaDD}/*.matrix.mtx.gz"):
    fn = ff.split("/")[-1]
    sm_id = ff.split("/")[-1].split(".")[0]

    files = [ff]
    for sufx in [".features.tsv.gz", ".barcodes.tsv.gz"]:
        eff = f"{yoonHaDD}/{sm_id}{sufx}"
        assert os.path.isfile(eff)
        if sufx == ".features.tsv.gz":
            files.append((eff, f"{sm_id}{sufx}.orig"))
        else:
            files.append(eff)

    print(sm_id, sm_id)

    tissue_sc, batch_n, organ, pcw_age = sm_id.split("_")

    assert tissue_sc[0] == "T"

    assert batch_n[0] == "b"
    batch_n = int(batch_n[1:])

    assert pcw_age.startswith("PCW")
    pcw_age = int(pcw_age[3:])

    print(sm_id, tissue_sc, batch_n, organ, pcw_age)


    resource_id = f"summary/liu2026Multiomics/sample_cell_expression_matrix/{sm_id}"
    conf = {
        "type": "ann_data",
        "file": f"{sm_id}.matrix.mtx.gz",
        # "features_file": f"{sm_id}.features.tsv.gz",
        # "barcodes_file": f"{sm_id}.barcodes.tsv.gz",
        "meta": {
            "summary": f"Sample cell expression matrix for {sm_id} from liu2026Multiomics.",
            "description": dedent("""
                [Liu, et al, Multiomics and deep learning dissect regulatory syntax in human development, Nature 2026.](https://www.nature.com/articles/s41586-026-10326-9)

                Downloaded from: [https://zenodo.org/records/15066651](https://zenodo.org/records/15066651).
            """),
            "labels": {
                "assay": "cell_expression",
                "technology": "SHARE-seq",
                "tissue_storage_code": tissue_sc,
                "exp_batch": batch_n,
                "organ": organ,
                "pcw_age": pcw_age,
                "dataset": "liu2026Multiomics"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)

    features_file = f"{get_resource_dir(resource_id)}/{sm_id}.features.tsv.gz"
    if os.path.isfile(features_file):
        continue
    features_file_orid = f"{get_resource_dir(resource_id)}/{sm_id}.features.tsv.gz.orig"
    with gzip.open(features_file_orid, "rt") as IF:
        with gzip.open(features_file, "wt") as OF:
            for l in IF:
                cs = l.strip("\n\r").split("\t")
                assert len(cs) == 2
                print(*cs, "Gene Expression", sep="\t", file=OF)
 
