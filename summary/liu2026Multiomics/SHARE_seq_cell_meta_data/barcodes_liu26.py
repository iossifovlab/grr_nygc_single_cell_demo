"""
Create the Liu 2026 annotated-cell barcode resource.

Author-provided per-cell metadata supply the cell identifier and cluster
assignment. The identifier is split into sample and barcode, and Supplementary
Table S2 is used to map each Cluster to L1, L2, and L3 cell-type annotations.

Set RUN_EXTENDED_VALIDATION = True to verify all annotated barcodes against
the RNA-expression matrices and ATAC-fragment resources in the GRR. 

Normal resource generation uses only the source files stored in this directory.
Extended validation requires the GAIn environment and access to the GRR and may take a substantial amount of time because ATAC-fragment resources are checked across all 76 samples.
"""

import pandas as pd


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

RUN_EXTENDED_VALIDATION = False

METADATA_FILE = "per_cell_meta.csv"
S2_FILE = "S2.xlsx"
S2_SHEET = "Sheet1"

OUTPUT_FILE = "liu2026_annotated_barcode_namespace.csv.gz"

DATASET = "summary/liu2026Multiomics"

EXPECTED_ROWS = 817740
EXPECTED_SAMPLES = 76
EXPECTED_CLUSTERS = 203
EXPECTED_L1 = 203
EXPECTED_L2 = 134
EXPECTED_L3 = 37


# ------------------------------------------------------------
# Load per-cell metadata
# ------------------------------------------------------------

M = pd.read_csv(
    METADATA_FILE,
)

required_metadata_columns = [
    "cb",
    "Cluster",
    "organ_code",
]

missing = [
    column
    for column in required_metadata_columns
    if column not in M.columns
]

assert not missing, (
    f"Missing per-cell metadata columns: {missing}"
)

assert M["cb"].notna().all()
assert M["Cluster"].notna().all()

# Each identifier must contain exactly one "#" separator.
#
# Example:
# T166_b15_Liver_PCW19#CL105_H01+A01+A01
#
# ->
# sample  = T166_b15_Liver_PCW19
# barcode = CL105_H01+A01+A01

assert M["cb"].astype(str).str.count("#").eq(1).all(), (
    "Unexpected cb identifier format"
)

M[
    [
        "sample",
        "barcode",
    ]
] = (
    M["cb"]
    .astype(str)
    .str.split("#", n=1, expand=True)
)

# Preserve the original author-provided identifier.
M = M.rename(
    columns={
        "cb": "cb_Zenodo",
    }
)


# ------------------------------------------------------------
# Load Supplementary Table S2
#
# S2 contains one row per Cluster and provides:
#
#   L1_annot = most detailed annotation
#   L2_annot = intermediate annotation
#   L3_annot = broadest annotation
# ------------------------------------------------------------

S2 = pd.read_excel(
    S2_FILE,
    sheet_name=S2_SHEET,
)

required_s2_columns = [
    "Cluster",
    "organ_code",
    "L1_annot",
    "L2_annot",
    "L3_annot",
]

missing = [
    column
    for column in required_s2_columns
    if column not in S2.columns
]

assert not missing, (
    f"Missing S2 columns: {missing}"
)

assert S2["Cluster"].notna().all()

assert S2["Cluster"].is_unique, (
    "Cluster is not unique in S2"
)


# ------------------------------------------------------------
# Validate cluster namespace
# ------------------------------------------------------------

metadata_clusters = set(
    M["Cluster"].astype(str)
)

s2_clusters = set(
    S2["Cluster"].astype(str)
)

assert metadata_clusters == s2_clusters, (
    "Cluster sets differ between per-cell metadata and S2. "
    f"Only in metadata: {sorted(metadata_clusters - s2_clusters)}; "
    f"only in S2: {sorted(s2_clusters - metadata_clusters)}"
)


# ------------------------------------------------------------
# Add cell-type annotations
# ------------------------------------------------------------

annotations = S2[
    [
        "Cluster",
        "L1_annot",
        "L2_annot",
        "L3_annot",
    ]
].copy()

OUT = M.merge(
    annotations,
    on="Cluster",
    how="left",
    validate="many_to_one",
)

# Add harmonized class column shared across barcode resources.
# Keep the original Cluster and L1/L2/L3 annotation columns as well.
OUT["class"] = OUT["L1_annot"]

OUT = OUT[
    [
        "sample",
        "cb_Zenodo",
        "barcode",
        "class",
        "Cluster",
        "L1_annot",
        "L2_annot",
        "L3_annot",
    ]
]

# ------------------------------------------------------------
# Fast validation
# ------------------------------------------------------------

for column in OUT.columns:

    assert OUT[column].notna().all(), (
        f"Missing values in {column}"
    )

    assert (
        OUT[column]
        .astype(str)
        .str.strip()
        .ne("")
        .all()
    ), f"Blank values in {column}"


assert OUT["cb_Zenodo"].is_unique, (
    "cb_Zenodo is not unique"
)

assert not OUT[
    [
        "sample",
        "barcode",
    ]
].duplicated().any(), (
    "Duplicate sample/barcode pairs found"
)


assert len(OUT) == EXPECTED_ROWS, (
    f"Unexpected row count: {len(OUT)}"
)

assert OUT["sample"].nunique() == EXPECTED_SAMPLES, (
    f"Unexpected sample count: {OUT['sample'].nunique()}"
)

assert OUT["Cluster"].nunique() == EXPECTED_CLUSTERS, (
    f"Unexpected cluster count: {OUT['Cluster'].nunique()}"
)

assert OUT["L1_annot"].nunique() == EXPECTED_L1, (
    f"Unexpected L1 count: {OUT['L1_annot'].nunique()}"
)

assert OUT["L2_annot"].nunique() == EXPECTED_L2, (
    f"Unexpected L2 count: {OUT['L2_annot'].nunique()}"
)

assert OUT["L3_annot"].nunique() == EXPECTED_L3, (
    f"Unexpected L3 count: {OUT['L3_annot'].nunique()}"
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------
# Rename the harmonized sample column for the final resource.
OUTPUT = OUT.rename(columns={"sample": "sample_id"})

OUTPUT.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("Rows:", len(OUT))
print("Samples:", OUT["sample"].nunique())
print("Clusters:", OUT["Cluster"].nunique())
print("L1 annotations:", OUT["L1_annot"].nunique())
print("L2 annotations:", OUT["L2_annot"].nunique())
print("L3 annotations:", OUT["L3_annot"].nunique())

print("\nSaved:", OUTPUT_FILE)

print("\nFirst rows:")
print(
    OUTPUT.head()
    .to_string(index=False)
)


# ============================================================
# Extended validation
#
# This is not required to generate the resource. It requires
# GAIn/GRR access and checks every annotated barcode against
# the corresponding RNA-expression matrix and ATAC fragments.
#
# Previous exploratory validation (2026-09-24):
#
#   Example identifier:
#     T166_b15_Liver_PCW19#CL105_H01+A01+A01
#
#   Parsed as:
#     sample  = T166_b15_Liver_PCW19
#     barcode = CL105_H01+A01+A01
#
#   This barcode was found unchanged in both the RNA-expression
#   matrix and ATAC-fragment resource for the sample.
#
#   Cluster LI_2 was also confirmed to map through S2 to:
#
#     L1_annot = LI_2_erythroblast 1
#     L2_annot = Liver erythroblast
#     L3_annot = erythroblasts
#
# The validation below performs the barcode check exhaustively
# across all 76 samples.
# ============================================================

if RUN_EXTENDED_VALIDATION:

    import gzip

    from gain.genomic_resources.repository_factory import (
        build_genomic_resource_repository,
    )
    from gain.genomic_resources.ann_data_resource import (
        load_ann_data_from_resource,
    )

    print("\nRunning extended validation...")

    grr = build_genomic_resource_repository()

    rna_found = 0
    rna_missing = 0
    rna_missing_examples = []

    atac_found = 0
    atac_missing = 0
    atac_missing_examples = []


    grouped = list(
        OUT.groupby(
            "sample",
            sort=True,
        )
    )

    for i, (sample, D) in enumerate(
        grouped,
        start=1,
    ):

        expected = set(
            D["barcode"].astype(str)
        )

        print(
            f"[{i}/{len(grouped)}] {sample}"
        )


        # ----------------------------------------------------
        # RNA-expression matrix
        # ----------------------------------------------------

        rna_resource = grr.get_resource(
            f"{DATASET}/rna_expression_matrix/{sample}"
        )

        A = load_ann_data_from_resource(
            rna_resource,
            matrix_free=True,
        )

        rna_barcodes = set(
            A.obs_names.astype(str)
        )

        missing = expected - rna_barcodes

        rna_found += (
            len(expected) - len(missing)
        )

        rna_missing += len(missing)

        if missing and len(rna_missing_examples) < 10:

            remaining = (
                10 - len(rna_missing_examples)
            )

            rna_missing_examples.extend(
                [
                    (sample, barcode)
                    for barcode in sorted(missing)[
                        :remaining
                    ]
                ]
            )


        # ----------------------------------------------------
        # ATAC fragments
        # ----------------------------------------------------

        atac_resource = grr.get_resource(
            f"{DATASET}/atac_fragments/{sample}"
        )

        filename = (
            atac_resource
            .get_config()["table"]["filename"]
        )

        found = set()

        with atac_resource.open_raw_file(
            filename,
            mode="rb",
        ) as raw:

            with gzip.open(
                raw,
                mode="rt",
            ) as f:

                for line in f:

                    if line.startswith("#"):
                        continue

                    fields = (
                        line.rstrip("\n")
                        .split("\t")
                    )

                    barcode = fields[3]

                    if barcode in expected:

                        found.add(barcode)

                        # Stop once all annotated barcodes
                        # for this sample have been found.
                        if len(found) == len(expected):
                            break

        missing = expected - found

        atac_found += len(found)
        atac_missing += len(missing)

        if missing and len(atac_missing_examples) < 10:

            remaining = (
                10 - len(atac_missing_examples)
            )

            atac_missing_examples.extend(
                [
                    (sample, barcode)
                    for barcode in sorted(missing)[
                        :remaining
                    ]
                ]
            )


    # --------------------------------------------------------
    # Extended-validation results
    # --------------------------------------------------------

    print("\nRNA-expression matrix validation:")
    print("Expected:", EXPECTED_ROWS)
    print("Found:", rna_found)
    print("Missing:", rna_missing)

    if rna_missing_examples:
        print(
            "Missing examples:",
            rna_missing_examples,
        )


    print("\nATAC fragment validation:")
    print("Expected:", EXPECTED_ROWS)
    print("Found:", atac_found)
    print("Missing:", atac_missing)

    if atac_missing_examples:
        print(
            "Missing examples:",
            atac_missing_examples,
        )


    assert rna_found == EXPECTED_ROWS
    assert rna_missing == 0

    assert atac_found == EXPECTED_ROWS
    assert atac_missing == 0

    print("\nExtended validation passed.")

else:
    print("\nExtended validation: OFF")