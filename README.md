
# GRR NYGC Single-Cell Demo

This repository organizes data from selected single-cell studies as Genomic Resource Repository (GRR) resources. GRRs are part of the GAIn framework and provide a consistent way to organize and access genomic data, including gene expression matrices, chromatin accessibility data, and cell and sample metadata.

For more information, see the [GAIn preprint](https://doi.org/10.64898/2026.07.08.737273) and the [GRR documentation](https://iossifovlab.com/gaindocs/grr.html).

## Clone the repository

Clone the repository from GitHub:

```bash
git clone git@github.com:iossifovlab/grr_nygc_single_cell_demo.git
cd grr_nygc_single_cell_demo
```

## Environment setup

The repository provides two Conda environment files: one for accessing and analyzing genomic resources and another for managing the repository. Conda or Mamba is required.

### General user environment

The `environment.yaml` file provides the packages needed to browse and analyze genomic resources using GAIn. It includes `gain-core`, IPython, JupyterLab, and dependencies for the Dask dashboard.

Create and activate the `gain` Conda environment:

```bash
mamba env create -f environment.yaml
conda activate gain
```

### Management environment

The `management_environment.yaml` file provides additional tools for managing genomic resources, including DVC and its Google Cloud Storage and SSH extensions.

Create and activate the `grr` Conda environment:

```bash
mamba env create -f management_environment.yaml
conda activate grr
```

Both environments include `gain-core`. Users can choose the environment appropriate for their work.

## Getting started locally

A local clone of the repository can be used to explore its directory structure, resource configurations, and metadata without downloading the large genomic data files.

The resources are organized under the `summary/` directory. To inspect the directory structure, run:

```bash
ls summary/
```

To browse the resources using GAIn, first create a GRR definition file pointing to the local repository. From the repository root, run:

```bash
cat > /tmp/nygc_grr.yaml <<EOF
id: nygc_single_cell
type: directory
directory: $(pwd)
EOF
```

This creates a temporary configuration file identifying the local repository.

To list the available single-cell resources, run:

```bash
grr_browse -g /tmp/nygc_grr.yaml -q 'summary/*'
```

GAIn can display resource types, identifiers, and metadata using the Git-tracked repository files. To analyze the underlying datasets, users need access to the data files, such as through the shared GRRs at NYGC or CSHL described below.

## Accessing data at NYGC and CSHL

At NYGC and CSHL, the single-cell datasets are available through existing GRRs on shared institutional storage. Users working on systems with access to these directories can analyze the data without downloading separate copies.

After activating the `gain` environment, set the `GRR_DEFINITION_FILE` environment variable to the appropriate configuration.

**At NYGC:**

```bash
export GRR_DEFINITION_FILE=/gpfs/commons/datasets/controlled/NYGC_AI_Initiative/GRRs/grr_definition.yaml
```

**At CSHL:**

```bash
export GRR_DEFINITION_FILE=/grid/iossifov/data/GRRs/grr_definition.yaml
```

To browse the available genomic resources:

```bash
grr_browse
```

### Accessing resources in Python

Once the GRR definition is configured, genomic resources can be accessed programmatically using GAIn:

```python
from gain.genomic_resources.repository_factory import build_genomic_resource_repository

grr = build_genomic_resource_repository()
```

The repository object can be used to locate and load individual resources by their resource IDs for downstream analyses.

Access to the underlying data requires appropriate filesystem permissions. The institutional paths above are not expected to be accessible from ordinary local computers.

For more information on working with genomic resources in Python, see the [GAIn documentation](https://iossifovlab.com/gaindocs/).

## Repository management

The repository is managed using Git, DVC, and `grr_manage`:

- **Git** tracks resource configurations, metadata, manifests, and DVC tracking files.
- **DVC** manages large genomic data files and their remote storage.
- **`grr_manage`** generates and updates resource manifests, statistics, and repository indexes.

Repository maintainers should use the `grr` Conda environment described above.

After adding or modifying genomic resources, the relevant management commands include:

```bash
# Track a new or modified large data file
dvc add path/to/data_file

# Update a resource's manifest and statistics
grr_manage resource-repair -r path/to/resource

# Rebuild manifests and statistics for the entire repository
grr_manage repo-repair
```

Updated resource configurations, DVC tracking files, and generated GRR metadata should be committed using Git. Managing large data files also requires appropriate access to the configured DVC remote.

For additional information about creating, modifying, and maintaining genomic resources, see the [GRR documentation](https://iossifovlab.com/gaindocs/grr.html).
