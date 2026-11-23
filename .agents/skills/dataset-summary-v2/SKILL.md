---
name: dataset-summary-v2
description: Investigate and create or improve a study's dataset_summary in the NYGC Single-Cell GRR using local DVC-backed data, verified evidence, and consistent researcher-oriented documentation.
---

# NYGC single-cell study dataset summaries

Create, reconstruct, or improve `summary/<study>/dataset_summary/genomic_resource.yaml` and its generated HTML. The result is a **researcher-facing guide to the data actually available in the GRR**, not a copy of the paper or a technical validation log. Follow the user's requested scope; investigate and present a proposal first if the user requests a review checkpoint.

## Task scope and safeguards

- For **new work or improving a stub**, read the existing target summary (if any), identify what is already correct, and preserve verified details and working links. For a **blind holdout**, do not consult any previous version of that study's summary through Git history, GitHub, institutional GRRs, cached HTML, or other copies. This restriction applies only to holdouts.
- Treat the Skill as the editorial standard. Read one or two **other complete** summaries if needed for repository-specific examples (prefer similar assay and layout); do not imitate incomplete stubs or assume that older examples are authoritative.
- Before editing, record `git --no-optional-locks status --short --untracked-files=all` and the current branch. Inventory resource YAMLs, manifests, statistics, DVC pointers, and existing data paths. Count **configured data resources**, excluding the `dataset_summary` itself; distinguish resource counts from files, indexes, and directories.
- Modify only the target `dataset_summary/` unless the user explicitly expands the scope. Do not commit, push, alter DVC pointers, fix other resource YAMLs, or run repository-wide repair without explicit authorization. Report defects found elsewhere separately.

## BAMdev: software, local GRR, and DVC are separate

The **Conda environment** supplies software; **DVC checkout** makes cached data available in the working tree; **`GRR_DEFINITION_FILE`** determines which repository GAIn reads. Do not confuse these steps.

Work from the user's local Git checkout, normally `~/grr_nygc_single_cell_demo`. Prefer its `grr` Conda environment for `dvc`, `grr_manage`, and analysis tools. Configure GAIn to use the local definition `~/nygc_grr_definition.yaml`, and **check that the YAML `directory` points to this checkout**, not institutional storage. Start with:

```bash
cd ~/grr_nygc_single_cell_demo
conda activate grr
export GRR_DEFINITION_FILE="$HOME/nygc_grr_definition.yaml"
git rev-parse --show-toplevel
command -v python grr_manage dvc
python -c 'import yaml; from pathlib import Path; p=Path.home()/"nygc_grr_definition.yaml"; d=yaml.safe_load(p.read_text()); print("GRR directory:", d.get("directory")); assert Path(d["directory"]).resolve()==Path.cwd().resolve()'
```

- Check the repo's machine-local `.dvc/config.local` and configured cache before changing DVC settings. On BAMdev the local cache has been configured to reuse shared CSHL data; preserve that configuration. **Use local data paths and explicit local GRR IDs** for inspection and verification. Never silently fall back to the shared institutional GRR when a local resource is unavailable.
- Check whether the *specific files needed* for the study exist in the working tree. If DVC-tracked files are absent but cached, restore only relevant targets, for example `dvc checkout --allow-missing -R "summary/<study>"` from the repo root; select narrower targets when practical. This does **not** download missing cache objects. `--allow-missing` can still leave outputs unavailable: check the required paths afterward and record gaps. Do not use `--force`, `dvc pull`, `dvc fetch`, `dvc push`, or reconfigure the cache without authorization. Don't checkout over user-modified files.
- If the `grr` environment lacks a required GAIn loader, identify an available compatible GAIn interpreter (on BAMdev, a shared GAIn Conda executable may be used as **software only**), while explicitly retaining `GRR_DEFINITION_FILE` for the local checkout. Verify resolution of an explicit study resource ID before proceeding. **Do not source `set_sc_v0.sh` or `set_sc_v1.sh` by default**: they configure institutional GRRs and may silently redirect inspection away from the working tree.
- Prefer resource statistics and read-only metadata access over copying or scanning large matrices and fragment files. Do not materialize whole studies unnecessarily. If a required data file cannot be accessed, state the limitation instead of inventing a result.

## Establish evidence before writing

1. **Publication and scope.** Identify the correct paper and its publication status; verify the full title, author, venue, year, and DOI (or versioned preprint). Check the study's biological question, major supported findings, assays, species, brain regions, cohort and controls. Distinguish experiments described by the **paper** from modalities and processed results **actually present in the GRR**. Mention an important paper-only assay if otherwise a claim or supplementary result would be misleading.
2. **Repository inventory.** Enumerate every top-level group and its configured descendant resources; inspect representative resource YAMLs, statistics, and supplementary table schemas. Verify what files contain: a raw 10x multimodal matrix is not automatically an RNA-only matrix; a deposit record containing separate RNA and ATAC files is not necessarily two records. Treat configuration descriptions as claims to check, not proof of actual modality, normalization, alignment patch, or processing method.
3. **Counts with explicit units.** Measure, when relevant, filtered/annotated **cells or nuclei**, raw matrix **observations**, biological **samples**, **donors**, specimens, libraries, files, feature counts, taxonomy levels, and pseudobulk tracks. Distinguish publication-wide totals from local, assay-specific, release-specific, and QC-filtered totals. Record `Unknown`/unassigned values when reporting classifications. Do not conflate fragment **rows** with summed **read support**, or files with libraries.
4. **Data access.** Resolve the study's resources by explicit ID using the **local** GRR definition. Use GAIn's loader for small data frames. For H5AD use a read-only backed loader (`anndata.read_h5ad(path, backed="r")` when working from the file) and inspect shapes, `obs`, `var`, and embedding names; close the handle. Avoid loading `X`, dense counts, or layers merely to establish an inventory. For HDF5 or Matrix Market resources inspect headers and metadata before considering expensive reads.
5. **Cross-resource joins.** Identify both fields in each join, their sample/library namespaces, and required prefixes/suffixes (such as `-1`, full cell IDs, or `sample_id#barcode`). Check uniqueness, overlaps, unmatched keys **in both directions**, and agreement in shared metadata. Validate sample-to-donor and metadata-to-matrix mappings. Distinguish file availability from barcode membership; do not infer equivalence from counts alone. If alternative classifications disagree, name the actual fields and quantify verified differences.
6. **ATAC fragment validation.** Prefer complete per-barcode histograms and precomputed per-contig statistics over full fragment scans. For compressed statistics, use the resource's raw-file interface before `gzip.GzipFile` when necessary. Confirm the histogram is complete, distinguish fragment rows and read support, and use a bounded tabix query only to check format and sample records. A tabix spot check does **not** establish whole-file barcode coverage.
7. **Claim ledger.** In investigation notes, record each important number or assertion with its **unit, cohort/scope, data release (if known), source, and validation method**. Separate publication claims, measured file facts, GRR metadata, and inference. Mark unverified normalization, genome-patch precision, file equivalence, or conflicting provenance explicitly; do not silently resolve such conflicts. Check that technical statements in resource descriptions are supported by the named files and configurations.

## Write the resource YAML

Create or update `summary/<study>/dataset_summary/genomic_resource.yaml` using `type: basic`, `meta.summary`, `meta.description: |`, and verified `meta.labels`. Use consistent **two-space YAML indentation**, clean spacing, and no trailing whitespace. Escape underscores inside bold Markdown names: `**rna\_expression\_matrix**`. Keep the description readable for scientists; put large validation tables, UUID inventories, detailed QC, and other audit evidence in the task notes unless essential for using the resources.

Use this order:

1. **Scientific introduction (two concise paragraphs).** First: question, context, and one or two well-supported scientific findings where appropriate, accurately attributed to the paper and its assays. Second: methods and **verified GRR dataset composition**, prioritizing comparable counts with named units. Include important distinctions between the study and the deposited subset; do not crowd the introduction with every feature dimension or validation statistic. Preserve useful study-specific context (e.g., age groups, anatomical structures, important cell taxonomy, or missing modalities) rather than shortening away facts researchers need.
2. **Publication reference.** Use first author + *et al.* for multi-author publications, **full exact title**, venue and year in both `meta.summary` and the linked citation. Prefer a published DOI; otherwise cite the relevant **versioned preprint**. Explain any essential release-specific choice or material discrepancy in the task report. Only add deposit links when they materially help understand or use the available GRR resources.
3. **Resource tree.** Use a monospace HTML `<pre>` tree and include **every configured top-level data resource or group**. Expand useful nested groups selectively. For large, naturally ordered sets, show the **first two**, `...`, and **exactly the last one**, except when a few extra examples are necessary to reveal a substantially different subgroup. Preserve numeric/natural ordering. Link the root through `../../../index.html#/summary/<study>`, directories through the GRR hash navigation, and leaves through their actual `index.html` paths **relative to the dataset_summary page**, including nested directories (e.g. `../supplementary_table/S3/3a/index.html`). Never use a group route for a leaf.
4. **Resource counts.** Every visible resource/group entry below the root gets an accurate count, including `1 resource` for a leaf. Group totals count all configured descendants, including hidden entries. Do not count the root or `...`. Align **the first digit** of each count based on visible text **after stripping HTML tags**; check rendered HTML as well as YAML. Ensure links within `<pre>` inherit the monospace font if page CSS would otherwise disrupt alignment.
5. **Resource descriptions.** Follow tree order. Start with the resource/group name in **bold**, describe its actual contents, useful annotations/fields, researcher uses, and correct cross-resource joins where applicable. Combine related entries in one paragraph only when clearer (e.g., matched ATAC/RNA pseudobulk tracks). Retain verified distinctions that affect use: filtered vs raw, label vocabularies, missing counterpart libraries, available age strata, and processing/release limitations. Include a compact correspondence table only if it genuinely simplifies a nontrivial mapping not already easy to retrieve from metadata; avoid redundant or oversized tables.
6. **Labels.** Include verified, applicable `assay`, `dataset`, `species`, `vendor`, `sequencing_platform`, `reference_genome`, and study-specific labels. Check all values against the local resources and schema. Use schema-supported lists for multi-valued labels; omit unknown/unsupported values rather than guessing. Do not assert a more precise genome build than the underlying processing evidence supports when describing methods.

## Scoped repair and validation

Before repair, parse the YAML and check each tree link/route against the local GRR. Run `grr_manage resource-repair -j 1` **from the target `dataset_summary/` directory**, using the local environment and definition. This conservative job setting applies only to the small **basic summary resource**; do not reuse it for large matrix or ATAC resource repairs. Check `grr_manage resource-repair --help` if the installed version requires other syntax. Never run `repo-repair` for this task.

Verify and report all of the following:

- Repair **exit status** and any warnings; manifest-update warnings may be benign but the **final** YAML/HTML/statistics entries must match their manifest hashes and sizes.
- Rendered study introduction, full citation, resource descriptions, escaped underscores, tables, nested links, and tree counts/alignment; resolve relative leaf-page links and hash navigation **separately**. Verify statistics HTML and stats hash. Distinguish static link checks from browser navigation actually tested.
- Scientific numbers, field names, and join claims against investigation evidence. Record checks that cover the **full dataset** separately from spot checks and unverified claims.
- `git status --short`, `git diff --check`, and changes against the baseline. Only intended summary files may change. Do not stage, commit, push, or alter unrelated resources unless requested.

Finish with a brief report: generated/updated paths, data and publication sources consulted, verified counts and joins, validation performed, unresolved questions, and Git changes. **For production work, ask for human scientific/editorial review before committing or pushing.** If validation exposes a serious inconsistency, flag it rather than publishing a stronger claim than the evidence supports.
