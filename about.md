# This is a prototype Genomic Resource Repository for single-cell data aggregated by the NYGC for their machine-learning initiative


# These are the studies:

* [johansen2025Crossspecies](./summary/johansen2025Crossspecies/summary/index.html)

* [liu2026Multiomics](./summary/liu2026Multiomics/summary/index.html)

* [zemke2023Conserved](./summary/zemke2023Conserved/summary/index.html)

* [zemke2024Epigenetic](./summary/zemke2024Epigenetic/summary/index.html)



# Definition of the Used Labels



| Label                     | Short definition                                                                                          | Allowed values / examples                                                                    | Example                          |
| ------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------- |
| **`vendor`**              | Organization that developed/provides the experimental technology or assay system.                         | `10x_Genomics`, `Bio-Rad`, `Parse_Biosciences`, `unknown`                                    | `10x_Genomics`                   |
| **`assay`**               | Specific experimental protocol or assay used to generate the biological data.                             | `10x_Multiome`, `10x_3prime_GEX`, `10x_ATAC`, `snm3C-seq`, `scRNA-seq`, `scATAC-seq`         | `10x_Multiome`                   |
| **`sequencing_platform`** | Instrument/platform used to sequence the resulting libraries. This is distinct from the assay technology. | `Illumina`, `PacBio`, `Oxford_Nanopore`, `unknown`                                           | `Illumina`                       |
| **`resolution`**          | Biological unit at which the measurements are represented.                                                | `bulk`, `single_cell`, `single_nucleus`, `cell_type`, `pseudo_bulk_cell_type`                | `single_nucleus`                 |
| **`modalities`**          | Molecular measurement(s) represented in the dataset. **Can contain multiple values.**                     | `RNA`, `ATAC`, `DNA_methylation`, `3D_genome`, `protein`, etc.                               | `[RNA, ATAC]`                    |
| **`data_types`**          | Specific type of data within each modality. **Can contain multiple values.**                              | `gene_expression`, `peak_counts`, `fragments`, `CpG_methylation`, `chromatin_contacts`, etc. | `[gene_expression, peak_counts]` |
| **`file_format`**         | Format in which the data are stored.                                                                      | `h5ad`, `h5`, `mtx`, `tsv`, `bed`, `bedGraph`, `pairs`, `bigWig`, etc.                       | `h5ad`                           |
| **`processing_level`**    | Degree to which the raw sequencing data have been processed.                                              | `raw`, `processed`, `normalized`, `annotated`, `aligned`, `RPKM_normalized`                  | `processed`                      |
| **`dataset`**             | The dataset the resource belongs to.                                                                      | `zemke2023Conserved`, `liu2026Multiomics`                                                    | `liu2026Multiomics`              |
| **`species`**             | The species the resource belongs to.                                                                      | `human`, `macaque`, `marmoset`, `mouse`                                                      | `human`                          |
| **`brain_region`**        | The brain region.                                                                                         | `m1`, `mop`                                                                                  | `m1`                             |
