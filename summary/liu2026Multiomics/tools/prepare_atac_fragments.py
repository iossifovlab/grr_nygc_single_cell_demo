import glob, os
from pathlib import Path
from typing import Any
import yaml
from textwrap import dedent


repo_dir = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR"


def prepapre_resrouce(resource_id: str, files: list[str],
                      config: dict[str, Any]):
    resource_dir = repo_dir + "/" + resource_id
    os.makedirs(resource_dir, exist_ok=True)

    for rf in files:
        remote_file = Path(rf)
        target_dir = Path(resource_dir)

        symlink_path = target_dir / remote_file.name
        if os.path.isfile(symlink_path):
            continue
        symlink_path.symlink_to(remote_file)

    with open(resource_dir + "/genomic_resource.yaml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)


yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/HDMA/ATAC_RNA"


for ff in glob.glob(f"{yoonHaDD}/*.fragments.tsv.gz"):
    iff = ff + ".tbi"
    assert os.path.isfile(iff)


    fn = ff.split("/")[-1]
    sm_id = ff.split("/")[-1].split(".")[0]
    print(sm_id, sm_id)

    tissue_sc, batch_n, organ, pcw_age = sm_id.split("_")

    assert tissue_sc[0] == "T"

    assert batch_n[0] == "b"
    batch_n = int(batch_n[1:])

    assert pcw_age.startswith("PCW")
    pcw_age = int(pcw_age[3:])

    print(sm_id, tissue_sc, batch_n, organ, pcw_age)

    resource_id = f"summary/liu2026Multiomics/sample_atac_fragments/{sm_id}"
    files = [ff, iff]
    conf = {
        "type": "basic",
        "file": ff.split("/")[-1],
        "index_file": iff.split("/")[-1],
        "meta": {
            "summary": f"Sample ATAC fragments for {sm_id} from liu2026Multiomics.",
            "description": dedent("""
                [Liu, et al, Multiomics and deep learning dissect regulatory syntax in human development, Nature 2026.](https://www.nature.com/articles/s41586-026-10326-9)

                Downloaded from: [https://zenodo.org/records/15066651](https://zenodo.org/records/15066651).

                Genomic coordinates in fragment files are 0-based.
            """),
            "labels": {
                "assay": "atac_fragmets",
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

