import glob
import yaml
import os

import pandas as pd
import scipy.io
import anndata as ad
import scanpy as sc


def mtx_file_to_dir_and_prefix(mtx_file_name: str) -> tuple[str, str | None]:
    dr = os.path.dirname(mtx_file_name)
    fn = os.path.basename(mtx_file_name)
    if not fn.endswith("matrix.mtx.gz"):
        raise Exception("wrong suffice for an mtx file.")
    pref = fn[:-13]
    if pref == "":
        pref = None
    return dr, pref


def load_by_sample_matrix(mtx_file: str) -> ad.AnnData:
    dr, prf = mtx_file_to_dir_and_prefix(mtx_file)
    adata = sc.read_10x_mtx(
        dr,
        prefix=prf,
        var_names="gene_ids",
        gex_only=False,
        make_unique=False
    )

    features_file = mtx_file.replace("matrix.mtx.gz", "features.tsv.gz")

    features = pd.read_csv(
        features_file,
        sep="\t",
        header=None,
        names=[
            "gene_id",
            "gene_symbol",
            "feature_type",
            "chrom",
            "start",
            "end",
        ],
    )

    features = features.set_index("gene_id")
    adata.var = adata.var.join(features.drop(columns=["gene_symbol", "feature_type"]), how="left")

    return adata


def load_by_species_matrix(mtx_file: str) -> ad.AnnData:
    features_file = mtx_file.replace("matrix.mtx.gz", "features.tsv.gz")
    barcodes_file = mtx_file.replace("matrix.mtx.gz", "barcodes.tsv.gz")
    metadata_file = mtx_file.replace("matrix.mtx.gz", "metadata.tsv.gz")

    X = scipy.io.mmread(mtx_file).tocsr()

    var = pd.read_csv(features_file, sep="\t", header=None, names=["gene"], index_col=0)

    obs_names = pd.read_csv(barcodes_file, sep="\t", header=None, names=["cell"])["cell"]

    obs = pd.read_csv(metadata_file, sep="\t").set_index("cell")
    assert list(obs.index) == list(obs_names)
    # obs = obs.loc[obs_names]

    adata = ad.AnnData(X=X.T, obs=obs, var=var)

    return adata


for mtxfp in glob.glob("../RNAmatrix/*/*_raw_feature_bc_matrix.h5"):
    parts = mtxfp.split("/")
    mtxfn = parts[-1]
    oid = parts[-2]

    print(oid, mtxfn)

    parts[-1] = "genomic_resource.yaml"
    grc = "/".join(parts)

    with open(grc, "r") as stream:
        old_config = yaml.safe_load(stream)

    config = {}
    config["type"] = "ann_data"
    config["file"] = mtxfn
    config["meta"] = old_config["meta"]

    with open(grc, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)


