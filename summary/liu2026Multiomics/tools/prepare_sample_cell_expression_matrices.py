import glob
import os
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/HDMA/ATAC_RNA"

for ff in glob.glob(f"{yoonHaDD}/*.matrix.mtx.gz"):
    fn = ff.split("/")[-1]
    sm_id = ff.split("/")[-1].split(".")[0]

    files = []
    for sufx in [".features.tsv.gz", ".barcodes.tsv.gz"]:
        eff = f"{yoonHaDD}/{sm_id}{sufx}"
        assert os.path.isfile(eff)
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
        "type": "basic",
        "file": f"{sm_id}.matrix.mtx.gz",
        "features_file": f"{sm_id}.features.tsv.gz",
        "barcodes_file": f"{sm_id}.barcodes.tsv.gz",
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
    # prepapre_resrouce(resource_id, files, conf)

