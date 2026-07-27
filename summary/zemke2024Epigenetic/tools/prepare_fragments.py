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

    files = [ff, indx_fn]

    resource_id = f"summary/zemke2024Epigenetic/ATACfragments/{individual_id}"
    print(resource_id)

    conf = {
        "type": "basic",
        "file": fn,
        "index_file": indx_fn,
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
