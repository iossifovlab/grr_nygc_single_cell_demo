#!/usr/bin/env python

import os
import glob
import subprocess
from urllib.request import urlretrieve

# download_url_prefix="ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE229nnn/GSE229169/suppl"

download_url_prefix="https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE229169&format=file&file="
supplementary_files = '''
GSE229169_barcodes.tar.gz
GSE229169_features.tar.gz
GSE229169_human_filtered_barcodes.tsv.gz
GSE229169_human_filtered_features.tsv.gz
GSE229169_human_filtered_matrix.mtx.gz
GSE229169_human_filtered_metadata.tsv.gz
GSE229169_macaque_filtered_barcodes.tsv.gz
GSE229169_macaque_filtered_features.tsv.gz
GSE229169_macaque_filtered_matrix.mtx.gz
GSE229169_macaque_filtered_metadata.tsv.gz
GSE229169_marmoset_filtered_barcodes.tsv.gz
GSE229169_marmoset_filtered_features.tsv.gz
GSE229169_marmoset_filtered_matrix.mtx.gz
GSE229169_marmoset_filtered_metadata.tsv.gz
GSE229169_matrix.tar.gz
GSE229169_mouse_filtered_barcodes.tsv.gz
GSE229169_mouse_filtered_features.tsv.gz
GSE229169_mouse_filtered_matrix.mtx.gz
GSE229169_mouse_filtered_metadata.tsv.gz
'''

os.makedirs("./GSE229169_download_buff", exist_ok=True)
for sf in supplementary_files.split("\n"):
    if sf == "":
        continue
    url = download_url_prefix + "/" + sf
    local_file = "./GSE229169_download_buff" + "/" + sf
    if os.path.isfile(local_file):
        continue

    try:
        print(f"DOWNLOADING {url} to {local_file}")
        urlretrieve(url, local_file)
        print("DOWNLOAD OK: ", url)
    except Exception as e:
        print("DOWNLOAD FAILED: ", url)
        print(f"DOWNLOAD FAILED: {url}+suffix\n{e}\n\n\n")
        assert False

os.makedirs("./GSE229169_tar_buff", exist_ok=True)
for tarf in glob.glob("GSE229169_download_buff/*.tar.gz"):
    fn = os.path.basename(tarf)
    if os.path.isfile(f"./GSE229169_tar_buff/{fn}.flag"):
        continue
    command = f"tar -xvf {tarf} -C GSE229169_tar_buff && touch GSE229169_tar_buff/{fn}.flag"
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=False)
    assert result.returncode == 0

for dr, tp, features, fltr in [["GSE229169_download_buff", "by_species", "genes", "filtered"],
                               ["GSE229169_tar_buff", "by_sample", "genes_and_atac_peaks", "raw"]]:
    print(dr, tp, features, fltr)
    for mtx_file in glob.glob(f"{dr}/*_matrix.mtx.gz"):
        files = [mtx_file,
                 mtx_file.replace("_matrix.mtx.gz", "_features.tsv.gz"),
                 mtx_file.replace("_matrix.mtx.gz", "_barcodes.tsv.gz")]
        for file in files:
            assert os.path.isfile(file)
        mt_file = mtx_file.replace("_matrix.mtx.gz", "_metadata.tsv.gz")
        if os.path.isfile(mt_file):
            files.append(mt_file)
        if fltr == "filtered":
            s_id = mtx_file.split("/")[-1].split("_")[1]
        else:
            s_id = mtx_file.split("/")[-1][:-14]
        res_dir = f"../cell_expression/{tp}/{s_id}"
        os.makedirs(res_dir, exist_ok=True)
        print("\t", mtx_file, len(files), res_dir)

        resource_config_str = f'''
type: basic


meta:
  summary: "Cell Expression Matrix {tp} for {s_id} with {features} features"

  description: |

    [Zemke, et al, Conserved and divergent gene regulatory programs of the
    mammalian neocortex, Nature 2023.](https://www.nature.com/articles/s41586-023-06819-6)

    Downloaded from:

    [https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE229169](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE229169)
  labels:
    assay: cell_expression
'''
        with open(f"{res_dir}/genomic_resource.yaml", "w", encoding="utf-8") as RCF:
          print(resource_config_str, file=RCF, end="")

        for file in files:
            rfn = res_dir + "/" + os.path.basename(file)
            if os.path.isfile(rfn):
                continue
            command = f"ln {file} {rfn}"
            print(f"Running: {command}")
            result = subprocess.run(command, shell=True, capture_output=False)
            assert result.returncode == 0
            
        # print("\t\t", ",".join(files))

