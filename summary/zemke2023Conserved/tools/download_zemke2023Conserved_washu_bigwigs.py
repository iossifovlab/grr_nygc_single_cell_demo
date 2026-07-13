#!/usr/bin/env python

import os
from urllib.request import urlretrieve

cell_types_def_str = '''
ODC        \tnon-neuron\tOligodendrocyte\tOGC
OPC        \tnon-neuron\tOligodendrocyte precursor cell
ASC        \tnon-neuron\tAstrocyte
MGC        \tnon-neuron\tMicroglial cell
Endo       \tnon-neuron\tEndothelial cell
VLMC       \tnon-neuron\tVascular and leptomeningeal cell
L6_IT_CAR3 \texcitatory\tLayer 6 intratelencephalic (CAR3+) excitatory neuron
L4_5_IT    \texcitatory\tLayer 4/5 intratelencephalic excitatory neuron
L2_3_IT    \texcitatory\tLayer 2/3 intratelencephalic excitatory neuron
L6b        \texcitatory\tLayer 6b excitatory neuron
L6_CT      \texcitatory\tLayer 6 corticothalamic excitatory neuron
L6_IT      \texcitatory\tLayer 6 intratelencephalic excitatory neuron
L5_6_NP    \texcitatory\tLayer 5/6 near-projecting excitatory neuron
L5_IT      \texcitatory\tLayer 5 intratelencephalic excitatory neuron
L5_ET      \texcitatory\tLayer 5 extratelencephalic excitatory neuron
ChC        \tinhibitory\tChandelier cell
LAMP5      \tinhibitory\tLAMP5-positive inhibitory interneuron
PVALB      \tinhibitory\tParvalbumin-positive inhibitory interneuron
SNCG       \tinhibitory\tSynuclein gamma-positive inhibitory interneuron
SST        \tinhibitory\tSomatostatin-positive inhibitory interneuron
VIP        \tinhibitory\tVasoactive intestinal peptide-positive inhibitory interneuron
'''

# A few notes:

# IT = intratelencephalic-projecting excitatory neuron.
# ET = extratelencephalic-projecting (formerly "PT") excitatory neuron.
# CT = corticothalamic excitatory neuron.
# NP = near-projecting excitatory neuron.
# ChC = chandelier cell, an axo-axonic inhibitory interneuron.
# LAMP5, PVALB, SNCG, SST, and VIP are canonical inhibitory interneuron classes named after their marker genes.
# VLMC stands for vascular and leptomeningeal cell, a non-neuronal cell associated with blood vessels and meninges.


CELL_TYPES = {}

for ctds in cell_types_def_str.strip().split("\n"):
    if ctds == '':
        continue
    cs = [v.strip() for v in ctds.split("\t")]
    if len(cs) == 3:
        ct_id, ct_type, ct_desc = cs
        ct_other_id = None
    elif len(cs) == 4:
        ct_id, ct_type, ct_desc, ct_other_id = cs
    else:
        assert False
    assert ct_id not in CELL_TYPES
    CELL_TYPES[ct_id] = (ct_desc, ct_type, ct_other_id)

SPECIES_RGN = ["human_m1", "macaque_m1", "marmoset_m1", "mouse_mop"]
TRACKS = ["atac", "rna"]

LF = open("log_file", "a")

ui = -1
uit = len(SPECIES_RGN) * len(TRACKS) * len(CELL_TYPES)
for species_rgn in SPECIES_RGN:
    for track in TRACKS:
        for cell_type, cell_type_atts in CELL_TYPES.items():
            ui += 1
            other_id = cell_type_atts[2]
            cell_type_remote = cell_type
            if other_id is not None:
                cell_type_remote = other_id
            url = f"https://epigenome.wustl.edu/renlab/{species_rgn}_{track}/{cell_type_remote}_{track.upper()}_RPKM.bw"
            url_md = url.replace("_", '\\_')
            local_dir = f"../pseudo_bulk_{track}_bw/{species_rgn}/{cell_type}"
            local_file_name = f"{cell_type}_{track.upper()}_RPKM.bw"
            score = f"zemke2023Conserved_{species_rgn}_{cell_type}_{track}_rpkm"
            local_file = local_dir + "/" + local_file_name

            # Download
            # if not os.path.isfile(local_file):
            #     os.makedirs(local_dir, exist_ok=True)

            #     print(f"Working on URL ({ui}/{uit}): {url}...")
            #     try:
            #         urlretrieve(url, local_file)
            #         print("DOWNLOAD OK: ", url)
            #     except Exception as e:
            #         print("DOWNLOAD FAILED: ", url)
            #         print(f"DOWNLOAD FAILED: {url}\n{e}\n\n\n", file=LF)
            #         continue

            if not os.path.isfile(local_file):
                continue
            resource_config_str = f'''type: position_score

table:
  filename: {local_file_name}
  chrom:
    index: 0
  pos_begin:
    index: 1
  pos_end:
    index: 2

# score values
scores:
  - id: {score}
    type: float
    desc: "Pseudo-bulk RPKM {track} in {species_rgn} for {cell_type} cell type"
    index: 3
    histogram:
      type: number
      number_of_bins: 100
      y_log_scale: True
      x_log_scale: True
      x_min_log: 0.00001



meta:
  summary: "Pseudo-bulk {track} track in {species_rgn} for {cell_type} cell type"

  description: |

    [Zemke, et al, Conserved and divergent gene regulatory programs of the
    mammalian neocortex, Nature 2023.](https://www.nature.com/articles/s41586-023-06819-6)

    Downloaded from:

    [{url_md}]({url})
  labels:
    species: {species_rgn.split("_")[0]}
    cell_type: {cell_type}
    assay: {track}
    brain_region: {species_rgn.split("_")[1]}

'''
            with open(f"{local_dir}/genomic_resource.yaml", "w", encoding="utf-8") as RCF:
                print(resource_config_str, file=RCF, end="")
LF.close()
