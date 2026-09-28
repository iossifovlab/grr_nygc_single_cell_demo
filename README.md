# GRR NYGC Single-Cell Demo

Genomic Resource Repositories (GRRs) provide a framework for organizing and accessing genomic data resources in a consistent format. GRRs can contain many types of genomic information, including position-, interval-, gene-, and matrix-based resources. The GAIn framework and supported resource types are described in our [preprint](https://doi.org/10.64898/2026.07.08.737273), while the [GRR documentation](https://iossifovlab.com/gaindocs/index.html) explains how to interact with existing GRRs and how to construct new repositories.

Single-cell technologies make it possible to characterize molecular features at the level of individual cells. For example, single-cell RNA sequencing (scRNA-seq) measures gene expression in individual cells, while single-cell ATAC-seq (scATAC-seq) measures chromatin accessibility at single-cell resolution. Increasingly, studies generate multiple types of molecular data from the same biological samples or cells, creating both opportunities and challenges for integrating these datasets.

This repository collects data from selected single-cell studies and organizes them as GRR resources. The goal is to provide a consistent representation of expression matrices, chromatin accessibility data, cell and sample metadata, and other associated resources. Organizing these datasets within a common GRR framework facilitates access to the different data types and their integration across resources and studies.

## Included studies

- **Johansen 2025** — Cross-species single-cell RNA and metadata.
- **Liu 2026** — Single-cell RNA and ATAC multiomics.
- **Zemke 2023** — Single-cell RNA and ATAC data.
- **Zemke 2024** — Single-cell expression, ATAC, and metadata.
