import glob
import os
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce

yoonHaDD = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/HDMA/bigwigs/3-bigwigs"

for ff in glob.glob(f"{yoonHaDD}/*/*.bw"):
    fn = ff.split("/")[-1]
    fn_parts = fn.split(".")[0].split("_")
    assert len(fn_parts) == 6
    assert fn_parts[2] == ''

    dir_parts = ff.split("/")[-2].split("_")
    assert len(dir_parts) == 2
    assert dir_parts[0] == fn_parts[0] and dir_parts[1] == fn_parts[1]

    measure = "_".join(fn_parts[3:])
    # print(fn_parts, measure, fn, ff)

    organ, cluster_id = fn_parts[:2]

    files = [ff]

    descriptions = {
        "obs_pval_signal": "Macs2 p-value signal track for observed accessibility",
        "mean_pred_corrected": "bias-corrected accessibility predicted by ChromBPNet",
        "mean_counts_contribs": "base-resolution contribution scores for the counts head of ChromBPNet as computed by DeepLIFT"
    }

    histograms = {
        "obs_pval_signal": {
                "type": "number",
                "number_of_bins": 100,
                "y_log_scale": True,
                "x_log_scale": False,
            },
        "mean_pred_corrected": {
                "type": "number",
                "number_of_bins": 100,
                "y_log_scale": True,
                "x_log_scale": True,
                "x_min_log": 0.00001
            },
        "mean_counts_contribs": {
                "type": "number",
                "number_of_bins": 100,
                "y_log_scale": True,
                "x_log_scale": False,
            }
    }
    print(organ, cluster_id, measure)
    resource_id = f"summary/liu2026Multiomics/bigwig/{organ}/{cluster_id}/{measure}"
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
            "id": f"liu2026Multiomics_{organ}_{cluster_id}_{measure}",
            "type": "float",
            "desc": descriptions[measure],
            "index": 3,
            "histogram": histograms[measure]
        }],
        "meta": {
            "summary": f"{measure} for {organ} for cell cluster {cluster_id}",
            "description": dedent("""
                [Liu, et al, Multiomics and deep learning dissect regulatory syntax in human development, Nature 2026.](https://www.nature.com/articles/s41586-026-10326-9)

                Downloaded from: [https://zenodo.org/records/15066651](https://zenodo.org/records/15066651).
                Description of the data and download instructions can be found [https://github.com/GreenleafLab/HDMA/blob/main/DATA.md](https://github.com/GreenleafLab/HDMA/blob/main/DATA.md)
            """),
            "labels": {
                "assay": "pseudo_bulk_atac",
                "technology": "SHARE-seq",
                "organ": organ,
                "cluster": f"{organ}_{cluster_id}",
                "dataset": "liu2026Multiomics"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
