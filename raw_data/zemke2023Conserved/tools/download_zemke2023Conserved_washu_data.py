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

ui = 0
uit = len(SPECIES_RGN) * len(TRACKS) * len(CELL_TYPES)
for species_rgn in SPECIES_RGN:
    for track in TRACKS:
        for cell_type, cell_type_atts in CELL_TYPES.items():
            other_id = cell_type_atts[2]
            cell_type_remote = cell_type
            if other_id is not None:
                cell_type_remote = other_id
            url = f"https://epigenome.wustl.edu/renlab/{species_rgn}_{track}/{cell_type_remote}_{track.upper()}_RPKM.bw"
            local_dir = f"../pseudo_bulk_{track}_bw/{species_rgn}_{cell_type}"
            local_file_name = f"{cell_type}_{track.upper()}_RPKM.bw"

            os.makedirs(local_dir, exist_ok=True)

            print(f"Working on URL ({ui}/{uit}): {url}...")
            try:
                urlretrieve(url, local_dir + "/" + local_file_name)
                print("DOWNLOAD OK: ", url)
            except Exception as e:
                print("DOWNLOAD FAILED: ", url)
                print(f"DOWNLOAD FAILED: {url}\n{e}\n\n\n", file=LF)
                print("")
            ui += 1
            # https://epigenome.wustl.edu/renlab/macaque_m1_rna/L5_ET_RNA_RPKM.bw

LF.close()