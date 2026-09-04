# This is a prototype Genomic Resource Repository for single-cell data aggregated by the NYGC for their machine-learning initiative

# Definition of the Used Labels


### Score definitions


| Label                     | Short definition                                                                                          | Allowed values / examples                                                                    | Example                          |
| ------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------- |
| **`vendor`**              | Organization that developed/provides the experimental technology or assay system.                         | `10x_Genomics`, `Bio-Rad`, `Parse_Biosciences`, `unknown`                                    | `10x_Genomics`                   |
| **`assay`**               | Specific experimental protocol or assay used to generate the biological data.                             | `10x_Multiome`, `10x_3prime_GEX`, `10x_ATAC`, `snm3C-seq`, `scRNA-seq`, `scATAC-seq`         | `10x_Multiome`                   |
| **`sequencing_platform`** | Instrument/platform used to sequence the resulting libraries. This is distinct from the assay technology. | `Illumina`, `PacBio`, `Oxford_Nanopore`, `unknown`                                           | `Illumina`                       |
| **`resolution`**          | Biological unit at which the measurements are represented.                                                | `bulk`, `single_cell`, `single_nucleus`, `cell_type`                                         | `single_nucleus`                 |
| **`modalities`**          | Molecular measurement(s) represented in the dataset. **Can contain multiple values.**                     | `RNA`, `ATAC`, `DNA_methylation`, `3D_genome`, `protein`, etc.                               | `[RNA, ATAC]`                    |
| **`data_types`**          | Specific type of data within each modality. **Can contain multiple values.**                              | `gene_expression`, `peak_counts`, `fragments`, `CpG_methylation`, `chromatin_contacts`, etc. | `[gene_expression, peak_counts]` |
| **`file_format`**         | Format in which the data are stored.                                                                      | `h5ad`, `h5`, `mtx`, `tsv`, `bed`, `bedGraph`, `pairs`, `bigWig`, etc.                       | `h5ad`                           |
| **`processing_level`**    | Degree to which the raw sequencing data have been processed.                                              | `raw`, `processed`, `normalized`, `annotated`                                                | `processed`                      |
