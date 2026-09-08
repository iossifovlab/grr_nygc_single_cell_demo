import glob
import os, gzip
from textwrap import dedent
from collections import Counter
import pandas as pd
import os
import yaml
from pathlib import Path
from typing import Any

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

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/zemke2023_extra"

meta = pd.read_csv(f"{yoonHaDD}/metadata_2026-08-09-23h-34m.tsv", comment='#', sep="\t")
file2meta = {s.iloc[0].split('/')[-1]:s.to_dict() for n,s in meta.iterrows()}

def get_metadata_from_file(filename):
    with gzip.open(filename, "rt") as f:
        for line in f:
            if line.startswith("# id="):
                s_id = line.strip('\n').split('=')[1]
                break
    return s_id

for ff in glob.glob(f"{yoonHaDD}/*.tsv.gz"):
    fn = ff.split("/")[-1]

    meta_info = file2meta[fn]
    individual_id = get_metadata_from_file(ff)

    indx_fn = ff + ".tbi"
    assert os.path.isfile(indx_fn)

    print(ff, fn, individual_id)

    draw_file = "../../tools//fragment_count_dist_plot.py"
    files = [ff, indx_fn, draw_file]


    resource_id = f"summary/zemke2023Conserved/ATACfragments/{individual_id}"
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
            "summary": f"ATAC fragments for {individual_id} from zemke2023Conserved.",
            "description": dedent("""

            [Zemke, et al, Conserved and divergent gene regulatory programs of the
            mammalian neocortex, Nature 2023.](https://www.nature.com/articles/s41586-023-06819-6)

            Downloaded from: [https://data.4dnucleome.org/publications/8d4e8d7c-b98f-4857-a4c1-274dfc39817a/#expsets-table](https://data.4dnucleome.org/publications/8d4e8d7c-b98f-4857-a4c1-274dfc39817a/#expsets-table).
            """),
            "labels": {
                "assay": meta_info['File Type'], #"atac_fragments",
                "technology": meta_info["Experiment Type"],
                "individual_id": individual_id,
                "organism": meta_info["Organism"],
                "dataset": f"zemke2023Conserved - {meta_info['Dataset']}"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)