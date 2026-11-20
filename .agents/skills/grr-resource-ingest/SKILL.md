---
name: grr-resource-ingest
description: Inspect downloaded scientific data and create, repair, and validate individual genomic resources in the NYGC Single-Cell GRR. Use dataset-summary for study overview pages.
---

# Ingest genomic resources

## Inspect the download

- Inventory filenames, sizes, and companion files. Identify formats using file signatures, headers, schemas, or format-aware readers. Use bounded reads and record what they establish about dimensions, columns, coordinate conventions, identifiers, and annotations.
- Open H5AD with `anndata.read_h5ad(path, backed="r")` for inspection. Check shape, observation and feature metadata, and embeddings without loading the expression matrix. Close the backed handle. For indexed interval files, inspect the index and sample a few bounded queries. Use index counts or complete existing statistics when available. Report sampled checks as such.
- Verify assay, modality, species, reference assembly, and other labels from the file, deposit, or publication as applicable. Omit claims that the evidence cannot establish.

## Choose the layout and create the resource

- Find comparable `genomic_resource.yaml` files in other GRR studies. Compare the resource type, study-wide or per-sample placement, relative file references, format options, required sidecars, metadata labels, and generated artifacts. For unfamiliar formats, confirm the chosen pattern against the installed GAIn loader or schema when examples are ambiguous.
- Record Git status before editing. Create one leaf directory per logical resource under `summary/<study>/`, following the applicable examples. For instance, a study-wide H5AD commonly lives in `rna_expression_matrix/` as `type: ann_data` with a relative `file`. A Tabix-indexed ATAC table commonly lives in `atac_fragments/` as `type: fragment_score`, with a `table` mapping and score columns derived from the actual file.
- Copy the payload and required sidecars into the leaf directory and preserve the original downloads. Keep files directly in the resource directory unless DVC is explicitly requested. Check copied sizes and use available checksums or the repair-generated manifest to avoid redundant full reads of large payloads.
- Write and parse `genomic_resource.yaml`. Verify that configured paths resolve, the loader supports the format, and columns and coordinate settings match the data. Include verified provenance and labels using repository conventions.

## Repair and validate

- Use the GAIn environment documented in the repository README for the checkout's GRR release. Verify the `grr_manage` executable and Python import. Run `grr_manage resource-repair` from each new resource directory. Keep repair scoped to those resources.
- Start with the installed tool's defaults. For large files, check `grr_manage resource-repair --help` and adjust workers or region size to fit available CPU, memory, and I/O. Keep bounded regions when they enable GAIn's vectorized scan. A single worker or unbounded regions can make fragment statistics substantially slower. Use those settings only when the workload or environment calls for them. Let repair generate required statistics and avoid a separate full scan for inspection or validation.
- Capture the repair exit status and warnings. Check the final manifest against its named files, using file sizes, small-file hashes, and recorded payload digests where available. Verify that the statistics fingerprint and outputs match the current inputs. Reconcile applicable totals with independent evidence such as matrix dimensions, per-contig counts, or the Tabix index. Keep fragment row counts distinct from summed read support.
- Inspect the generated resource and statistics HTML and resolve local links. Build a read-only GAIn repository explicitly pointing at the working checkout, resolve the new resource by ID, and exercise the appropriate loader or a bounded indexed query. Verify that the loader reaches the local copy.
- Compare Git status with the baseline. Report the resources and files created, validation results, warnings, and gaps. Keep dataset summaries in the separate `dataset-summary` workflow.
