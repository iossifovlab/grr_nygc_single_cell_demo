#!/usr/bin/env python


from collections import defaultdict
from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository
import subprocess

try:
    grr
except NameError:
    grr = build_genomic_resource_repository()


org_to_genome_id = {
    'mouse': 'reference/Mouse/genome/GRCm39',
    'human': 'reference/Human/genome/ucsc-hg38',
    'macaque': 'reference/Macaque/genome/Mmul_10',
    'marmoset': 'reference/Marmoset/genome/calJac240_pri'
}

org_to_gene_model_id = {
    'mouse': 'reference/Mouse/gene_models/GRCm39_basic',
    'human': 'reference/Human/gene_models/GENCODE/49/basic/ALL',
    'macaque': 'reference/Macaque/gene_models/Mmul_10_NCBI_RefSeq',
    'marmoset': 'reference/Marmoset/gene_models/calJac240_pri_NCBI_RefSeq'
}


for r in grr.search_resources(resource_query="summary/zemke2023Conserved/single_nuclei_expression_and_atac_peaks/*"):
    species = r.get_labels()["species"]
    assert species in {"human", "mouse", "macaque", "marmoset"}

    id_parts = r.get_id().split("/")
    sub_dir = "/".join(id_parts[3:])

    labels = {
        "reference_genome": org_to_genome_id[species],
        "gene_models": org_to_gene_model_id[species],
    }
    labels_s = "{" + ", ".join(f"{k}: '{v}'" for k, v in labels.items()) + "}"

    cmd = f'add_labels.py "{labels_s}" ./{sub_dir}'
    print(species, sub_dir, r.get_id(), )
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    print(result.stdout)
    print()
