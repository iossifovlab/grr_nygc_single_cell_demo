---
name: dataset-summary
description: Create, reconstruct, or repair a study's dataset_summary in the NYGC Single-Cell GRR using verified study data and repository conventions.
---

# Study dataset summaries

Identify the target under `summary/<study>/`. Follow the requested scope. For an investigation-only request, report evidence and the proposed summary before changing files.

For independent reconstruction, use other studies as examples. Do not consult any previous version of the target summary, including copies in shared GRRs, Git history, GitHub, generated HTML, or cached catalog descriptions. Resolve the target's data resources by their explicit IDs to avoid retrieving its summary.

## Learn the repository conventions

Read several other studies' `dataset_summary/genomic_resource.yaml` files. Include a study with a similar assay and one with a similar directory layout. Note the scientific overview, citation style, YAML block scalars, labels, resource descriptions, and how leaf and group links differ. Use these examples for repository conventions and apply the editorial guidelines below. Derive target study facts from its own resources, publication, and deposits.

Inventory the target's resource YAMLs, manifests, DVC pointers, and current statistics. Count genomic resources by their configurations, rather than counting data files, indexes, or helper directories. Record a baseline with `git --no-optional-locks status --short --untracked-files=all` before editing so existing changes remain attributable.

## Use the shared GAIn environment on BAMdev

Consult the repository README for the institutional setup and match the configured GRR version to the working checkout. Check `command -v python grr_manage`, the value of `GRR_DEFINITION_FILE`, and `python -c 'import gain.grr'`. If the shared environment is missing or points to the wrong release, initialize it in the same Bash process that will run the inspection. On BAMdev (CSHL), the documented v1 setup is:

```bash
source /grid/iossifov/data/GRRs/set_sc_v1.sh
command -v python grr_manage
test -r "$GRR_DEFINITION_FILE"
python -c 'import gain.grr'
```

Use the README's v0 setup for a v0 checkout. If shell activation is unavailable, check the setup script for the shared environment's executable paths and exports. Use those executables with the matching GRR definition and other required settings. Confirm the repository resolves the intended data resources and report access gaps. Use the shared read-only GRR for data inspection and the working checkout for generation and repair.

## Verify the study and its data

- Use `gain.grr.build_genomic_resource_repository()` and resolve explicit IDs such as `summary/<study>/<resource>`. Inspect resource configuration and available statistics first. Load small tables with the GAIn data-frame loader. For H5AD, confirm the GAIn loader uses read-only backed mode, or resolve the local file and open it with `anndata.read_h5ad(..., backed="r")`. Read shape, observation and feature metadata, and embedding names as needed. Avoid reading `X`, raw counts, or layers for inventory. Close the backed handle.
- Establish the assay, organism, anatomy, cohort and controls from the paper and deposit. Measure the deposited matrix dimensions, unique samples and donors, and available annotations from the data. Verify joins, missing values, and sample-to-donor cardinality. Distinguish library and suspension IDs from biological sample IDs. Attribute differences between paper and repository totals to the available evidence.
- For paired modalities, compare unique full observation IDs and barcode namespaces, retaining sample or library suffixes. Check duplicate keys, intersection sizes, unmatched counts on both sides, and sample assignments. Test a documented mapping before transforming IDs. Report sample-level pairing or partial overlap if the evidence supports only that level.
- For ATAC fragments, prefer a complete per-barcode histogram over a full fragment scan. Check that it is the full artifact rather than a truncated preview. For a gzipped histogram, use `resource.open_raw_file(path, mode="rb")` before passing the stream to `gzip.GzipFile`. Cross-check histogram totals against per-contig statistics if available, and spot-check barcode syntax from a bounded tabix query. Tabix records returned by GAIn may be tuple-like, so use the configured barcode column index. A spot check verifies sampled records and cannot establish full barcode coverage by itself. Distinguish fragment rows from the summed read-support column.
- Record the evidence behind quantitative claims. Prepare a compact sample or modality correspondence table in the investigation notes when it helps verify how resources join.

## Write and repair

Create `summary/<study>/dataset_summary/genomic_resource.yaml` as `type: basic`. Use `meta.summary` for the study citation, `meta.description: |` for Markdown and the resource tree, and `meta.labels` for supported study labels. Match the local examples and verify labels against the target resources. Use verified study-level values when labels vary within the dataset.

Write `meta.description` for researchers using the available resources. Use clear scientific language and include details that help readers understand the dataset and use its resources. Follow this order.

1. **Scientific introduction.** Start with two concise paragraphs. In the first, explain the scientific question, study context, and major findings. In the second, describe the experimental approach and dataset composition. Include verified counts of cells or nuclei, samples, donors, and measured features where relevant to the assay.
2. **Publication reference.** Link the study publication immediately after the introduction. Include a deposit or other reference only when it supplies something essential for understanding or using the dataset.
3. **Resource tree.** Use a monospace HTML `<pre>` tree containing only linked resource names and counts. Link the study root through `../../../index.html#/summary/<study>`, individual resource pages through `../<resource>/index.html`, and group routes through the repository hash navigation as the examples do. Use singular and plural counts appropriately. Align the counts by measuring the visible lines after stripping HTML tags.
4. **Resource descriptions.** After the tree, write one short paragraph per resource group in tree order, including stand-alone resources at the same level. Begin each paragraph with the resource name in bold. Explain what it contains, what researchers can use it for, and how it relates to other resources when useful.

Keep sample correspondence tables, UUID listings, lengthy barcode statistics, detailed QC results, and technical validation evidence in the investigation notes or task report. Describe a verified relationship on the published page when it helps researchers use the resources.

Parse the YAML and verify the relative paths before repair.

From the target resource directory in the working checkout, run:

```bash
grr_manage resource-repair -j 1
```

Use `grr_manage resource-repair --help` if needed. The command locates the local repository and the resource from the current directory. Pass an explicit repository or resource argument only if discovery needs it. Keep repair scoped to this resource. Capture the exit status and warnings. A message that a manifest entry needs updating can occur during a successful repair. Verify that the final manifest reflects the current files.

## Validate the result

- Inspect the generated resource and statistics HTML, manifest entries, and stats hash. Compare the manifest hashes and sizes against the named files.
- Check that the introduction, publication link, tree, resource paragraphs, and any additional references, tables, or code spans rendered as intended. Check that count columns align in the generated `<pre>` text as well as the YAML. Resolve local HTML links relative to the page that contains them. Check the destination route for hash links separately from the existence of the root HTML file.
- Compare Git status with the baseline. A reconstruction can appear as staged deletions and untracked replacements at the same paths. Report this state and preserve the user's index. Leave unrelated resources and repository-wide indexes alone unless the user requests that scope.
- In the task report, describe what was generated, the technical findings and checks performed, warnings or errors, and any remaining issues.
