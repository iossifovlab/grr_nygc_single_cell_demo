
from collections import defaultdict
from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository
import subprocess

smp_by_atac = {}
smp_by_expr = {}
with open("sample_description.txt") as SDF:
    hcs = SDF.readline().strip("\n\r").split("\t")
    for l in SDF:
        cs = l.strip("\n\r").split("\t")
        assert len(cs) == len(hcs)
        R = dict(zip(hcs,cs))
        smp_by_expr[R["single_nuclei_expression_and_atac_peaks_by_sample_lp"]] = R
        smp_by_atac[R["ATACfragments_lp"]] = R


try:
    grr
except NameError:
    grr = build_genomic_resource_repository()


def proc_cmd(cmd: str):
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    print(result.stdout)
    print()


print("ATACfragments")
for r in grr.search_resources(resource_query="summary/zemke2023Conserved/ATACfragments/*"):
    lp = r.get_id().split("/")[-1]
    S = smp_by_atac[lp]
    labels = {
        "donor_id": S["donor_id"],
        "sample_id": S["sample_id / library_id"],
        "age": S["Age"],
        "sex": S["Sex"],
        "neun_enriched": S["neun_enriched"]
    }
    labels_s = "{" + ", ".join(f"{k}: '{v}'" for k, v in labels.items()) + "}"
    proc_cmd(f'add_labels.py "{labels_s}" ../../../{r.get_id()}')
    proc_cmd(f'del_labels.py individual_id ../../../{r.get_id()}')


print("single_nuclei_expression_and_atac_peaks/by_sample")
for r in grr.search_resources(resource_query="summary/zemke2023Conserved/single_nuclei_expression_and_atac_peaks/by_sample/*"):
    lp = r.get_id().split("/")[-1]
    S = smp_by_expr[lp]
    labels = {
        "donor_id": S["donor_id"],
        "sample_id": S["sample_id / library_id"],
        "age": S["Age"],
        "sex": S["Sex"],
        "species": S["Species"].lower(),
        "neun_enriched": S["neun_enriched"]
    }
    labels_s = "{" + ", ".join(f"{k}: '{v}'" for k, v in labels.items()) + "}"
    proc_cmd(f'add_labels.py "{labels_s}" ../../../{r.get_id()}')
    proc_cmd(f'del_labels.py sample ../../../{r.get_id()}')
