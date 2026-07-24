import glob
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/GSE278576"

cell_types = Counter()
age_ranges = Counter()
for ff in glob.glob(f"{yoonHaDD}/*.bw"):
    fn = ff.split("/")[-1]
    fn_parts = fn.split(".")[0].split("_")
    assert len(fn_parts) in [4, 3]
    assert fn_parts[0] == "GSE278576"
    assay = fn_parts[1]
    cell_type = fn_parts[2]
    age_range = "all" if len(fn_parts) == 3 else fn_parts[3]

    assert assay in ["RNA", "ATAC"]
    cell_types[cell_type] += 1
    age_ranges[age_range] += 1

    # print(ff, fn, fn_parts)

    files = [ff]

    resource_id = f"summary/zemke2024Epigenetic/{assay}/{cell_type}/{age_range}/bigwig"
    print(resource_id)
    conf = {
        "type": "position_score",
        "table": {
            "filename": fn,
            "chrom": {
                "index": 0
            },
            "pos_begin": {
                "index": 1
            },
            "pos_end": {
                "index": 2
            }
        },
        "scores": [{
            "id": f"zemke2024Epigenetic_{assay}_{cell_type}_{age_range}",
            "type": "float",
            "desc": "RPKM?",
            "index": 3,
            "histogram": {
                      "type": "number",
                      "number_of_bins": 100,
                      "y_log_scale": True,
            }
        }],
        "meta": {
            "summary": f"{assay} for {cell_type} cell type for age_range {age_range}",
            "description": dedent("""
                [Zemke et al., Epigenetic and 3D genome reprogramming during the aging of human hippocampus, bioRxiv, 2024](https://www.biorxiv.org/content/10.1101/2024.10.14.618338v1)

                Downloaded from: [https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278576](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278576).
            """),
            "labels": {
                "assay": assay,
                "technology": "10x genomics",
                "cell_type": cell_type,
                "age_range": age_range,
                "dataset": "zemke2024Epigenetic"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
