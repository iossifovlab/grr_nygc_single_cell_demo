import anndata as ad

fragment_h5ad_file = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/johansen2025Crossspecies/download/BasalGanglia_pre-print_ATAC/human/snapatac2/fe73a2757d8d05fbb09a5d1d9532eda0be0a40fa.h5ad"

big_expression_h5ad_file = "/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/AllenBrainMultiome/RNA/Human_HMBA_basalganglia_AIT_pre-print.h5ad"

# FAD = ad.read_h5ad(fragment_h5ad_file, backed="r")

EAD = ad.read_h5ad(big_expression_h5ad_file, backed="r")
