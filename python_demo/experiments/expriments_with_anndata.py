import os
import anndata as ad
import scanpy as sc


def assert_files_exist(fls: list[str]):
    for fl in fls:
        assert os.path.isfile(fl)


def proc_ann_data(dt: ad.AnnData):
    print(dt)
    if len(dt.obs.columns) > 0:
        print(dt.obs.describe())
    else:
        print("No observation columns")
    print(dt.var.describe())


def mtx_file_to_dir_and_prefix(mtx_file_name: str) -> tuple[str, str]:
    dr = os.path.dirname(mtx_file_name)
    fn = os.path.basename(mtx_file_name)
    if fn.endswith("matrix.mtx.gz"):
        pref = fn[:-13]
    elif fn.endswith("matrix.mtx"):
        pref = fn[:-10]
    else:
        raise Exception("wrong suffice for an mtx file.")
    if pref == "":
        pref = None
    return dr, pref


import numpy as np
import scipy.sparse as sp

def describe_adata(adata):
    print(f"AnnData: {adata.n_obs:,} obs × {adata.n_vars:,} vars\n")

    # --- X matrix summary ---
    X = adata.X
    is_sparse = sp.issparse(X)
    print("X matrix:")
    print(f"  dtype: {X.dtype}, sparse: {is_sparse}")
    if is_sparse:
        nnz = X.nnz
        density = nnz / (adata.n_obs * adata.n_vars)
        print(f"  non-zero entries: {nnz:,} (density: {density:.4%})")
        data = X.data
    else:
        data = X.flatten()
    print(f"  min/max: {data.min():.3g} / {data.max():.3g}")
    print(f"  mean/std (nonzero if sparse): {data.mean():.3g} / {data.std():.3g}")
    is_int_like = np.allclose(data, np.round(data))
    print(f"  looks like counts (integer values): {is_int_like}")

    # --- per-cell / per-gene stats ---
    counts_per_cell = np.asarray(X.sum(axis=1)).flatten()
    genes_per_cell = np.asarray((X > 0).sum(axis=1)).flatten()
    cells_per_gene = np.asarray((X > 0).sum(axis=0)).flatten()

    print("\nPer-cell stats:")
    print(f"  total counts: median={np.median(counts_per_cell):.0f}, "
          f"mean={counts_per_cell.mean():.1f}, range=[{counts_per_cell.min():.0f}, {counts_per_cell.max():.0f}]")
    print(f"  genes detected: median={np.median(genes_per_cell):.0f}, "
          f"mean={genes_per_cell.mean():.1f}")

    print("\nPer-gene stats:")
    print(f"  cells expressing: median={np.median(cells_per_gene):.0f}, "
          f"mean={cells_per_gene.mean():.1f}")
    print(f"  genes with zero expression: {(cells_per_gene == 0).sum():,} "
          f"({(cells_per_gene == 0).mean():.2%})")

    # --- obs / var metadata ---
    print(f"\nobs columns ({len(adata.obs.columns)}): {list(adata.obs.columns)}")
    print(f"var columns ({len(adata.var.columns)}): {list(adata.var.columns)}")

    print(f"\nlayers: {list(adata.layers.keys())}")
    print(f"obsm: {list(adata.obsm.keys())}")
    print(f"varm: {list(adata.varm.keys())}")
    print(f"uns keys: {list(adata.uns.keys())}")


# #################### DONE
# matrix_type = "johansen2025Crossspecies/pseudoBulk_expression_matrix"
# h5ad_file = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/AllenBrainMultiome/RNA/Human_HMBA_basalganglia_pseudobulk_aligned.h5ad"
# assert_files_exist([h5ad_file])
# adata = ad.read_h5ad(h5ad_file, backed="r")
# proc_ann_data(adata)
# adata.file.close()

# #################### DONE
# matrix_type = "johansen2025Crossspecies/cell_expression_matrix"
# h5ad_file = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/AllenBrainMultiome/RNA/Human_HMBA_basalganglia_AIT_pre-print.h5ad"
# assert_files_exist([h5ad_file])
# adata = ad.read_h5ad(h5ad_file, backed="r")
# proc_ann_data(adata)
# describe_adata(adata)
# adata.file.close()




# #################### DONE
# matrix_type = "zemke2023Conserved/cell_expression"

# features_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/zemke2023Conserved/cell_expression/by_sample/M1_Webster/M1_Webster_features.tsv.gz"
# barcodes_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/zemke2023Conserved/cell_expression/by_sample/M1_Webster/M1_Webster_barcodes.tsv.gz"
# mtx_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/zemke2023Conserved/cell_expression/by_sample/M1_Webster/M1_Webster_matrix.mtx.gz"
# assert_files_exist([features_file, barcodes_file, mtx_file])
# drr, pfx = mtx_file_to_dir_and_prefix(mtx_file)
# adata = sc.read_10x_mtx(drr, prefix=pfx)
# proc_ann_data(adata)
# adata.file.close()


#################### DONE after adding a third columns with "Gene Expression" values to the features files.
## zcat T233_b17_Thymus_PCW21.features.tsv.gz-orig | awk -F'\t' 'BEGIN{OFS="\t"}{print $1, $2, "Gene Expression"}' | gzip > T233_b17_Thymus_PCW21.features.tsv.gz
matrix_type = "liu2026Multiomics/sample_cell_expression_matrix"

features_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/liu2026Multiomics/sample_cell_expression_matrix/T233_b17_Thymus_PCW21/T233_b17_Thymus_PCW21.features.tsv.gz"
barcodes_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/liu2026Multiomics/sample_cell_expression_matrix/T233_b17_Thymus_PCW21/T233_b17_Thymus_PCW21.barcodes.tsv.gz"
mtx_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/liu2026Multiomics/sample_cell_expression_matrix/T233_b17_Thymus_PCW21/T233_b17_Thymus_PCW21.matrix.mtx.gz"
assert_files_exist([features_file, barcodes_file, mtx_file])
drr, pfx = mtx_file_to_dir_and_prefix(mtx_file)
adata = sc.read_10x_mtx(drr, prefix=pfx)
proc_ann_data(adata)
adata.file.close()





# #################### DONE
# matrix_type = "zemke2024Epigenetic/RNAmatrix"
# h5_file = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR/summary/zemke2024Epigenetic/RNAmatrix/hc77/GSE278576_hc77_raw_feature_bc_matrix.h5"
# assert_files_exist([h5_file])
# adata = sc.read_10x_h5(h5_file, gex_only=False)
# proc_ann_data(adata)
# adata.file.close()


