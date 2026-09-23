# This is a prototype Genomic Resource Repository for single-cell data aggregated by the NYGC for their machine-learning initiative

# Introduction

Git Rository [https://github.com/iossifovlab/grr\_nygc\_single\_cell\_demo](https://github.com/iossifovlab/grr_nygc_single_cell_demo)

Documentation [https://iossifovlab.com/gaindocs/](https://iossifovlab.com/gaindocs/)


# These are the studies:

* [johansen2025Crossspecies](./summary/johansen2025Crossspecies/dataset_summary/index.html)

* [liu2026Multiomics](./summary/liu2026Multiomics/dataset_summary/index.html)

* [zemke2023Conserved](./summary/zemke2023Conserved/dataset_summary/index.html)

* [zemke2024Epigenetic](./summary/zemke2024Epigenetic/dataset_summary/index.html)



# Definition of the Used Labels



| Label                     | Short definition                                                                                          | Allowed values / examples                                                                                                                      | Example                          |
| ------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| **`vendor`**              | Organization that developed/provides the experimental technology or assay system.                         | `10x_Genomics`, `Bio-Rad`, `Parse_Biosciences`, `Vizgen`, `unknown`                                                                            | `10x_Genomics`                   |
| **`assay`**               | Specific experimental protocol or assay used to generate the biological data.                             | `10x_Multiome`, `MERSCOPE`, `10x_ATAC`, `SHARE-seq`, `snm3C-seq`, `Patch-seq`, 'Xenium'                                                        | `10x_Multiome`                   |
| **`sequencing_platform`** | Instrument/platform used to sequence the resulting libraries. This is distinct from the assay technology. | `Illumina`, `PacBio`, `Oxford_Nanopore`, `unknown`                                                                                             | `Illumina`                       |
| **`resolution`**          | Biological unit at which the measurements are represented.                                                | `bulk`, `single_cell`, `single_nucleus`, `cell_type`, `pseudo_bulk_cell_type`                                                                  | `single_nucleus`                 |
| **`modalities`**          | Molecular measurement(s) represented in the dataset. **Can contain multiple values.**                     | `RNA`, `ATAC`, `DNA_methylation`, `3D_genome`, `protein`, etc.                                                                                 | `[RNA, ATAC]`                    |
| **`data_types`**          | Specific type of data within each modality. **Can contain multiple values.**                              | `gene_expression`, `peak_counts`, `fragments`, `atac_signal`, `atac_contribution`, `expression_signal`, `methylation signal`, `contact_signal` | `[gene_expression, peak_counts]` |
| **`file_format`**         | Format in which the data are stored.                                                                      | `h5ad`, `h5`, `mtx`, `tsv`, `bed`, `bedGraph`, `pairs`, `bigWig`, etc.                                                                         | `h5ad`                           |
| **`processing_level`**    | Degree to which the raw sequencing data have been processed.                                              | `raw`, `processed`, `normalized`, `annotated`, `aligned`, `RPKM_normalized`                                                                    | `processed`                      |
| **`dataset`**             | The dataset the resource belongs to.                                                                      | `zemke2023Conserved`, `liu2026Multiomics`                                                                                                      | `liu2026Multiomics`              |
| **`species`**             | The species the resource belongs to.                                                                      | `human`, `macaque`, `marmoset`, `mouse`                                                                                                        | `human`                          |
| **`brain_region`**        | The brain region.                                                                                         | `m1`, `mop`                                                                                                                                    | `m1`                             |
| **`organ`**               | Organ.                                                                                                    | `hear`, `lung`, `brain`                                                                                                                        | `heart`                          |


# GRR setup at NYGC and CSHL
```
$ mamba create –n gain  –c bioconda –c iossifovlab gain-core

$ conda activate gain

At NYGC:
$ export GRR_DEFINITION_FILE=/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/GRRs/grr_definition.yaml

At CSHL:
$ export GRR_DEFINITION_FILE=/grid/iossifov/data/GRRs/grr_definition.yaml (CSHL)

$ grr_browse --version
```
