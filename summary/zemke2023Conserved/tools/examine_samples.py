
from collections import defaultdict
from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository
import subprocess

try:
    grr
except NameError:
    grr = build_genomic_resource_repository()
ss = []

print("ATACfragments")
for r in grr.search_resources(resource_query="summary/zemke2023Conserved/ATACfragments/*"):
    lp = r.get_id().split("/")[-1]
    if lp.startswith("M1_"):
        sample_id = lp[3:]
    else:
        sample_id = lp
    species = r.get_labels()["species"]
    # ss.append(f'{lp:25} {species:20} {sample_id:20} {species:20}')
    ss.append(lp)

print("\n".join(sorted(ss)))

print("single_nuclei_expression_and_atac_peaks/by_sample")
bb = []
for r in grr.search_resources(resource_query="summary/zemke2023Conserved/single_nuclei_expression_and_atac_peaks/by_sample/*"):
    lp = r.get_id().split("/")[-1]
    bb.append(lp)
print("\n".join(sorted(bb)))