#!/usr/bin/env python

import os
from urllib.request import urlretrieve
import requests

from html.parser import HTMLParser
from urllib.parse import urljoin
import requests


# see download_zemke2023Conserved_washu_bedgraphs.py for description
cell_types = ['Astro',
 'CLA',
 'L23',
 'L4',
 'L5-ET',
 'L5-IT',
 'L6-CT',
 'L6-IT',
 'L6b',
 'Lamp5',
 'MG',
 'NP',
 'ODC',
 'OPC',
 'Pvalb-BC',
 'Pvalb-ChC',
 'Sncg',
 'Sst',
 'Vip',
 'Vsc']

SPECIES = "Human Macaque Marmoset Mouse".split()
URL_BASE = "https://epigenome.wustl.edu/renlab/hic"


LF = open("log_file", "a")

ui = -1
uit = len(SPECIES) * len(cell_types)
for species in SPECIES:
    for cell_type in sorted(cell_types):
        url = f"{URL_BASE}/{species}/{cell_type}.hic"
        url_md = url.replace("_", '\\_')
        local_dir = f"../pseudo_bulk_hic/{species}/{cell_type}"
        local_file_name = f"{cell_type}.hic"
        local_file = local_dir + "/" + local_file_name

        ui += 1
        if not os.path.isfile(local_file):
            os.makedirs(local_dir, exist_ok=True)

            print(f"Working on URL ({ui}/{uit}): {url} to {local_file}...")
            try:
                # urlretrieve(url, local_file)
                print("DOWNLOAD OK: ", url)
            except Exception as e:
                print("DOWNLOAD FAILED: ", url)
                print(f"DOWNLOAD FAILED: {url}+suffix\n{e}\n\n\n", file=LF)
                assert False
        resource_config_str = f'''
type: basic


meta:
  summary: "Pseudo-bulk hic track in {species} M1 region for {cell_type} cell type"

  description: |

    [Zemke, et al, Conserved and divergent gene regulatory programs of the
    mammalian neocortex, Nature 2023.](https://www.nature.com/articles/s41586-023-06819-6)

    Downloaded from:

    [{url_md}]({url})
  labels:
    species: {species}
    cell_type: {cell_type}
    assay: hic
    brain_region: M1
'''
        with open(f"{local_dir}/genomic_resource.yaml", "w", encoding="utf-8") as RCF:
          print(resource_config_str, file=RCF, end="")



LF.close()


