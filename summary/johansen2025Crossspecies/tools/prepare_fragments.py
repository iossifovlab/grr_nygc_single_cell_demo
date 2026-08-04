import glob
import os
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/johansen2025Crossspecies/download/fragments/BasalGanglia_pre-print_ATAC"


for ff in glob.glob(f"{yoonHaDD}/*/*/*.gz"):
    ff_parts = ff.split("/")
    fn = ff.split("/")[-1]
    library = fn[:-3]
    species = ff_parts[-3]

    assert ff_parts[-2] in ["snapatac2", "snaptac2"]

    indx_ff = ff + ".tbi"
    assert os.path.isfile(indx_ff)

    print(fn, library, ff, indx_ff)

    draw_file = os.path.abspath("./fragment_count_dist_plot.py")
    files = [ff, indx_ff, draw_file]


    resource_id = f"summary/johansen2025Crossspecies/fragment/{species}/{library}"
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
            "summary": f"ATAC fragments for {species} from library {library}",
            "description": dedent("""
                [Johansen et al., Cross-species consensus atlas of the primate basal ganglia, bioRxiv, 2025](https://www.biorxiv.org/content/10.64898/2025.12.15.694496v1)

                Downloaded from: [s3://hmba-bican-sharing-802451596237-us-west-2/BasalGanglia_pre-print_ATAC](s3://hmba-bican-sharing-802451596237-us-west-2/BasalGanglia_pre-print_ATAC).
            """),
            "labels": {
                "assay": "ATAC",
                "technology": "10x genomics",
                "library": library,
                "species": species,
                "dataset": "johansen2025Crossspecies"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
