import glob
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/GSE278576"

cell_types = Counter()
age_ranges = Counter()
for ff in glob.glob(f"{yoonHaDD}/*_raw_feature_bc_matrix.h5"):
    fn = ff.split("/")[-1]
    fn_parts = fn.split(".")[0].split("_")
    assert len(fn_parts) == 6
    assert fn_parts[0] == "GSE278576"
    individual_id = fn_parts[1]

    print(ff, fn, fn_parts)

    files = [ff]

    resource_id = f"summary/zemke2024Epigenetic/RNAmatrix/{individual_id}"
    print(resource_id)

    conf = {
        "type": "basic",
        "file": fn,
        "meta": {
            "summary": f"Sample cell expression matrix for {individual_id} from zemke2024Epigenetic.",
            "description": dedent("""
                [Zemke et al., Epigenetic and 3D genome reprogramming during the aging of human hippocampus, bioRxiv, 2024](https://www.biorxiv.org/content/10.1101/2024.10.14.618338v1)

                Downloaded from: [https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278576](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278576).
            """),
            "labels": {
                "assay": "cell_expression",
                "technology": "10x genomie",
                "individual_id": individual_id,
                "dataset": "zemke2024Epigenetic"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
