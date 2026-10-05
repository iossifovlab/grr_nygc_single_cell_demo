# binning_tool example

A small `binning_tool` run over this GRR's ATAC fragment resources. It
exercises the `fragment_score_binner` label convention:
`cell_meta_resource_id` and `sample_id` on each fragment resource, and
`sample_id`, `barcode` and `class` columns in its metadata table.

- `binning_example.yaml`: the run definition. It bins 100 kb across
  chr1:1-10,000,000 of `reference/Human/genome/ucsc-hg38` for three small
  zemke2024Epigenetic samples (pooled, then per sample) and one
  liu2026Multiomics sample (grouped by `L2_annot`, then ungrouped).
- `grr_definition.yaml`: the published GRR over HTTP. To use the NYGC or
  CSHL mirror instead, pass `-g $GRR_DEFINITION_FILE`.

It needs a gain with iossifovlab/gain#1741 (gain master after f7baccd74;
no release includes it yet as of 2026-10-05).

```bash
# Resolve every query and print the tracks, groups and warnings; writes nothing.
binning_tool binning_example.yaml -g grr_definition.yaml --dry-run

# Bin for real: writes binning_example.h5 (100 bins x 78 tracks), ~30 s over HTTP.
binning_tool binning_example.yaml -g grr_definition.yaml -j 4
```

The dry-run reports 18 groups for the zemke2024 entries (18 tracks
pooled, 53 per sample) and 6 groups for the liu2026 `L2_annot` entry.
Checks on the output:

- each pooled zemke2024 class track equals the sum of its per-sample
  tracks;
- in every bin, liu2026's grouped tracks sum to no more than its
  `all_cells` track. Fragments whose barcode is not an annotated cell
  reach no group.
