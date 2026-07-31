import glob
import os
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/GSE278576"

cell_types = Counter()
age_ranges = Counter()
for ff in glob.glob(f"{yoonHaDD}/*_atac_fragments.tsv.gz"):
    fn = ff.split("/")[-1]
    fn_parts = fn.split(".")[0].split("_")
    assert len(fn_parts) == 4
    run_id = fn_parts[0]
    individual_id = fn_parts[1]

    assert run_id.startswith("GSM")

    indx_fn = ff + ".tbi.gz"
    assert os.path.isfile(indx_fn)

    print(ff, fn, fn_parts)

    draw_file = os.path.abspath("./fragment_count_dist_plot.py")
    files = [ff, indx_fn, draw_file]


    resource_id = f"summary/zemke2024Epigenetic/ATACfragments/{individual_id}"
    print(resource_id)

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
            "summary": f"ATAC fragments for {individual_id} from zemke2024Epigenetic.",
            "description": dedent("""
                [Zemke et al., Epigenetic and 3D genome reprogramming during the aging of human hippocampus, bioRxiv, 2024](https://www.biorxiv.org/content/10.1101/2024.10.14.618338v1)

                Downloaded from: [https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278576](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278576).
            """),
            "labels": {
                "assay": "atac_fragments",
                "technology": "10x genomie",
                "individual_id": individual_id,
                "run_id": run_id,
                "dataset": "zemke2024Epigenetic"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
