import glob
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce
from collections import Counter

davidBigWigDir = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/AllenBrainMultiome/bigwigs"

for ff in glob.glob(f"{davidBigWigDir}/*/*.bw"):
    fn = ff.split("/")[-1]

    species = ff.split("/")[-2]
    cell_type = fn.split(".")[0]
    # print(species, cell_type, fn, ff)

    assert species in {"human", "macaque", "marmoset"}

    files = [ff]

    resource_id = f"summary/johansen2025Crossspecies/{species}/{cell_type}/bigwig"
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
            "id": f"johansen2025Crossspecies_atac_{species}_{cell_type}",
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
            "summary": f"ATAC big wig for {cell_type} cell type from {species}",
            "description": dedent("""
                [Johansen et al., Cross-species consensus atlas of the primate basal ganglia, bioRxiv, 2025](https://www.biorxiv.org/content/10.64898/2025.12.15.694496v1)

                Downloaded from: [s3://hmba-bican-sharing-802451596237-us-west-2/BasalGanglia_pre-print_ATAC](s3://hmba-bican-sharing-802451596237-us-west-2/BasalGanglia_pre-print_ATAC).
            """),
            "labels": {
                "assay": "ATAC",
                "technology": "10x genomics",
                "cell_type": cell_type,
                "species": species,
                "dataset": "johansen2025Crossspecies"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
