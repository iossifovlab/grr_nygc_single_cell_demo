import glob
import os
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce

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
    draw_file = os.path.abspath("./fragment_count_dist_plot.py")
    files = [ff, iff, draw_file]
    conf = {
        "type": "fragment_score",

        "table": {
            "filename": fn,
            "format": "tabix",
            "header_mode": "none",
            "zero_based": True,

            "chrom": {
                "column_index": 0
            },
            "pos_begin": {
                "column_index": 1
            },
            "pos_end": {
                "column_index": 2
            }
        },
        "scores": [
            {
                "id": "cell",
                "column_index": 3,
                "type": "str",
                "histogram": {
                    "type": "categorical",
                    "plot_function": "fragment_count_dist_plot.py:plot_fragment_per_cell_count",
                    "displayed_values_count": 5
                }
            },
            {
                "id": "count",
                "column_index": 4,
                "type": "int",
                "histogram": {
                    "type": "number",
                    "view_range": {
                        "min": 1,
                        "max": 20
                    },
                    "number_of_bins": 20
                }
            }
        ],
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

