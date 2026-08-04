
import glob
from textwrap import dedent
from prepare_resrouce import prepapre_resrouce


davidRNADir = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/AllenBrainMultiome/RNA"


for ff in glob.glob(f"{davidRNADir}/*_HMBA_basalganglia_AIT_pre-print.h5ad"):
    parts = ff.split("/")
    fn = parts[-1]
    species = fn.split("_")[0]

    print(species, fn)

    files = [ff]

    resource_id = f"summary/johansen2025Crossspecies/comprehensive_expression_matrix/{species}"
    print(resource_id)

    conf = {
        "type": "ann_data",
        "file": fn,
        "meta": {
            "summary": f"Comprehensive expression matrix for {species}",
            "description": dedent("""
                [Johansen et al., Cross-species consensus atlas of the primate basal ganglia, bioRxiv, 2025](https://www.biorxiv.org/content/10.64898/2025.12.15.694496v1)

                Downloaded from: [https://brain-map.org/our-research/cell-type-taxonomies/cross-species-basal-ganglia-taxonomy](https://brain-map.org/our-research/cell-type-taxonomies/cross-species-basal-ganglia-taxonomy).

            """),
            "labels": {
                "assay": "scRNASeq",
                "technology": "10x-Genomics",
                "species": species,
                "dataset": "johansen2025Crossspecies"
            }
        }
    }
    prepapre_resrouce(resource_id, files, conf)
