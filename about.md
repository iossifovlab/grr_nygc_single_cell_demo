# About the NYGC Single-Cell GRR

The NYGC Single-Cell Genomic Resource Repository (GRR) organizes genomic and single-cell multiomic data collected for the NYGC AI Initiative. Its purpose is to make datasets from different studies easier to discover, inspect, and use within a common framework.

GRRs are part of GAIn, a framework for annotating genetic variants, genomic positions, and intervals, as described in our [preprint](https://doi.org/10.64898/2026.07.08.737273). A GRR organizes data into *resources*, each identified by a path-like ID and accompanied by a definition describing its contents, format, and metadata. Further technical details are available in the [GRR documentation](https://iossifovlab.com/gaindocs/grr.html).

## Repository contents

The resources are organized under two top-level directories:

- **`summary`** contains study-specific datasets organized by publication, including RNA expression matrices, ATAC fragment files, pseudobulk chromatin-accessibility tracks, cell and sample metadata, and supplementary tables. Each study includes a `dataset_summary` resource that provides information about the publication and explains how its resources are organized. A `cell_metadata` resource contains cell barcodes and cell-type annotations, allowing cell-type information to be associated with different data resources within the study.

- **`reference`** contains reference genome assemblies and gene models for human, macaque, marmoset, and mouse. These resources are selected to correspond to the reference genomes and gene annotations used in the included studies.


## Included studies

- **Johansen 2025:** [Cross-species consensus atlas of the primate basal ganglia](index.html#/summary/johansen2025Crossspecies)
- **Liu 2026:** [Multiomics and deep learning dissect regulatory syntax in human development](index.html#/summary/liu2026Multiomics)
- **Zemke 2023:** [Conserved and divergent gene regulatory programs of the mammalian neocortex](index.html#/summary/zemke2023Conserved)
- **Zemke 2024:** [Epigenetic and 3D genome reprogramming during the aging of the human hippocampus](index.html#/summary/zemke2024Epigenetic)

## Browsing resources

Use **Table view** to search and filter resources by type, or **Hierarchical view** to navigate the repository's directory structure. Select a resource to inspect its description, data type, metadata, and available statistics. The search field supports SQLite full-text search syntax, including `AND`, `OR`, and quoted phrases.

## Metadata labels

Resources are annotated with a set of metadata labels that describe different aspects of their contents. These include the source study (`dataset`), biological context (`species`, `organ`, `brain_region`), experimental methods (`vendor`, `assay`, `sequencing_platform`), and data characteristics (`modalities`, `data_types`, `resolution`, `processing_level`, `file_format`). These labels help users identify and compare resources across studies. For example, someone interested in human ATAC-seq data could look for resources labeled `species: human` and `modalities: ATAC`, then use additional labels to distinguish among the available datasets. The table below defines each label and provides examples of its values.


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


## Data access

Large data files are managed separately from the Git-tracked resource definitions. For instructions on setting up the repository, accessing the underlying datasets, and examples of working with the resources, see the [NYGC Single-Cell GRR GitHub repository](https://github.com/iossifovlab/grr_nygc_single_cell_demo).
