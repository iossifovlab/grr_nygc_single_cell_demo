#!/usr/bin/env python

import os
from urllib.request import urlretrieve
import requests

from html.parser import HTMLParser
from urllib.parse import urljoin
import requests




bedgraphs_list_str = '''
Astro.CGN-both.bedgraph.gz
Astro.CHN-both.bedgraph.gz
CLA.CGN-both.bedgraph.gz
CLA.CHN-both.bedgraph.gz
L4.CGN-both.bedgraph.gz
L4.CHN-both.bedgraph.gz
L5-ET.CGN-both.bedgraph.gz
L5-ET.CHN-both.bedgraph.gz
L5-IT.CGN-both.bedgraph.gz
L5-IT.CHN-both.bedgraph.gz
L6-CT.CGN-both.bedgraph.gz
L6-CT.CHN-both.bedgraph.gz
L6-IT.CGN-both.bedgraph.gz
L6-IT.CHN-both.bedgraph.gz
L6b.CGN-both.bedgraph.gz
L6b.CHN-both.bedgraph.gz
L23.CGN-both.bedgraph.gz
L23.CHN-both.bedgraph.gz
Lamp5.CGN-both.bedgraph.gz
Lamp5.CHN-both.bedgraph.gz
MG.CGN-both.bedgraph.gz
MG.CHN-both.bedgraph.gz
NP.CGN-both.bedgraph.gz
NP.CHN-both.bedgraph.gz
ODC.CGN-both.bedgraph.gz
ODC.CHN-both.bedgraph.gz
OPC.CGN-both.bedgraph.gz
OPC.CHN-both.bedgraph.gz
Pvalb-BC.CGN-both.bedgraph.gz
Pvalb-BC.CHN-both.bedgraph.gz
Pvalb-ChC.CGN-both.bedgraph.gz
Pvalb-ChC.CHN-both.bedgraph.gz
Sncg.CGN-both.bedgraph.gz
Sncg.CHN-both.bedgraph.gz
Sst.CGN-both.bedgraph.gz
Sst.CHN-both.bedgraph.gz
Vip.CGN-both.bedgraph.gz
Vip.CHN-both.bedgraph.gz
Vsc.CGN-both.bedgraph.gz
Vsc.CHN-both.bedgraph.gz
'''


'''
Cell type	Brief description
Oligodendrocyte (ODC)	Glial cell that produces and maintains the myelin sheath around axons in the central nervous system.
Oligodendrocyte precursor cell (OPC)	Proliferative precursor that differentiates into oligodendrocytes and contributes to myelin repair.
Astrocyte (ASC)	Abundant glial cell that supports neurons, regulates neurotransmitters and ions, and helps maintain the blood–brain barrier.
Microglial cell (MGC)	Resident immune cell of the brain responsible for immune surveillance, phagocytosis, and inflammatory responses.
Endothelial cell (Endo)	Cell lining blood vessels that forms the vascular endothelium and contributes to the blood–brain barrier.
Vascular and leptomeningeal cell (VLMC)	Perivascular connective tissue cell associated with blood vessels and meninges, involved in extracellular matrix production.
Layer 2/3 intratelencephalic (L2/3 IT)	Excitatory pyramidal neuron in cortical layers 2–3 that projects primarily to other cortical areas.
Layer 4/5 intratelencephalic (L4/5 IT)	Excitatory pyramidal neuron spanning layers 4–5 that communicates with other cortical regions.
Layer 5 intratelencephalic (L5 IT)	Excitatory projection neuron in layer 5 that sends axons to cortical targets in both hemispheres.
Layer 5 extratelencephalic (L5 ET)	Large excitatory projection neuron in layer 5 that sends axons to subcortical targets such as the brainstem and spinal cord.
Layer 5/6 near-projecting (L5/6 NP)	Excitatory neuron in deep cortex with predominantly local or nearby cortical projections.
Layer 6 intratelencephalic (L6 IT)	Deep-layer excitatory neuron that projects mainly to cortical areas within the telencephalon.
Layer 6 corticothalamic (L6 CT)	Excitatory neuron that projects from layer 6 to the thalamus and modulates thalamocortical signaling.
Layer 6 IT CAR3 (L6 IT CAR3)	Subclass of layer 6 intratelencephalic neurons characterized by expression of the CAR3 marker gene.
Layer 6b (L6b)	Excitatory neuron in the deepest cortical layer, considered a remnant of the developmental subplate and involved in long-range cortical circuits.
Chandelier cell (ChC)	Specialized inhibitory interneuron that synapses onto the axon initial segments of pyramidal neurons, exerting powerful control over spike initiation.
LAMP5 interneuron (LAMP5)	Inhibitory interneuron enriched for LAMP5 expression, typically located in superficial cortical layers and involved in local inhibition.
Parvalbumin interneuron (PVALB)	Fast-spiking inhibitory interneuron that provides strong perisomatic inhibition and synchronizes cortical network activity.
Synuclein gamma interneuron (SNCG)	Diverse class of inhibitory interneurons expressing SNCG, often associated with long-range or specialized inhibitory functions.
Somatostatin interneuron (SST)	Inhibitory interneuron that primarily targets dendrites of pyramidal neurons, regulating synaptic integration.
VIP interneuron (VIP)	Inhibitory interneuron that preferentially inhibits other interneurons, thereby producing disinhibition of pyramidal neurons.

For your documentation, I'd also recommend slightly expanding a few abbreviations in the names themselves:

IT = Intratelencephalic-projecting
ET = Extratelencephalic-projecting (formerly "pyramidal tract")
CT = Corticothalamic
NP = Near-projecting
CAR3 = Carbonic anhydrase 3-positive
LAMP5 = Lysosomal-associated membrane protein 5-positive
PVALB = Parvalbumin-positive
SNCG = Synuclein gamma-positive
SST = Somatostatin-positive
VIP = Vasoactive intestinal peptide-positive

These descriptions are consistent with the nomenclature used in recent cortical cell atlases from the BRAIN Initiative Cell Census Network and BRAIN Initiative Cell Atlas Network.
'''


manual_bedgraph_gz_files = bedgraphs_list_str.strip().split("\n")
cell_types = {bggz[:-17].split(".")[0] for bggz in manual_bedgraph_gz_files}

SPECIES = "Human Macaque Marmoset Mouse".split()
URL_BASE = "https://epigenome.wustl.edu/renlab/mC"
MEASURES = ["CGN", "CHN"]

# ### Check that all species have the same cell type (or bedgraph files)
# class GZLinkParser(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.links = []

#     def handle_starttag(self, tag, attrs):
#         if tag == "a":
#             attrs = dict(attrs)
#             href = attrs.get("href")
#             if href and href.endswith(".bedgraph.gz"):
#                 self.links.append(href)


# for species in SPECIES:
#     species_page_str = requests.get(f"{URL_BASE}/{species}").text
#     parser = GZLinkParser()
#     parser.feed(species_page_str)
#     bedgraph_gz_files = parser.links

#     if bedgraph_gz_files != manual_bedgraph_gz_files:
#         print("AAAAA")
#         break
#     print(species, "is OK")

LF = open("log_file", "a")

ui = -1
uit = len(SPECIES) * len(cell_types) * len(MEASURES) * 2
for species in SPECIES:
    for cell_type in sorted(cell_types):
        for measure in MEASURES:
            url = f"{URL_BASE}/{species}/{cell_type}.{measure}-both.bedgraph.gz"
            url_md = url.replace("_", '\\_')
            local_dir = f"../pseudo_bulk_mc_bedgraph/{species}/{cell_type}/{measure}"
            local_file_name = f"{cell_type}.{measure}-both.bedgraph.gz"
            score = f"zemke2023Conserved_{species}_{cell_type}_{measure.lower()}_mc"
            local_file = local_dir + "/" + local_file_name

            # Download
            for suffix in ["", ".tbi"]:
                ui += 1
                if not os.path.isfile(local_file + suffix):
                    os.makedirs(local_dir, exist_ok=True)

                    print(f"Working on URL ({ui}/{uit}): {url+suffix} to {local_file + suffix}...")
                    try:
                        urlretrieve(url+suffix, local_file+suffix)
                        print("DOWNLOAD OK: ", url+suffix)
                    except Exception as e:
                        print("DOWNLOAD FAILED: ", url+suffix)
                        print(f"DOWNLOAD FAILED: {url+suffix}+suffix\n{e}\n\n\n", file=LF)
                        assert False
            resource_config_str = f'''
type: position_score

table:
  filename: {local_file_name}
  format: tabix

  header_mode: none
  zero_based: True

  chrom:
    index: 0
  pos_begin:
    index: 1
  pos_end:
    index: 2

scores:
  - id: {score}
    index: 3
    type: float


meta:
  summary: "Pseudo-bulk wc track in {species} M1 region for {cell_type} cell type"

  description: |

    [Zemke, et al, Conserved and divergent gene regulatory programs of the
    mammalian neocortex, Nature 2023.](https://www.nature.com/articles/s41586-023-06819-6)

    Downloaded from:

    [{url_md}]({url})
  labels:
    species: {species}
    cell_type: {cell_type}
    assay: single cell methylation
    brain_region: M1
'''
            with open(f"{local_dir}/genomic_resource.yaml", "w", encoding="utf-8") as RCF:
                print(resource_config_str, file=RCF, end="")



LF.close()


