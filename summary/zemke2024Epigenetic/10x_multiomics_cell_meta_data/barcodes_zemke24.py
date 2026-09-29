"""
Create the Zemke 2024 annotated-cell barcode resource.

Author-provided GEO cell metadata are used as the source of per-cell
subclass annotations. The sample name is taken from orig.ident, and the
GRR barcode is derived from the final underscore-separated component of
the original GEO cell identifier.

Set RUN_EXTENDED_VALIDATION = True to verify every annotated barcode
against the RNA+ATAC matrices and ATAC-fragment resources in the GRR.
Normal resource generation uses only the source files stored in this directory. 
Extended validation takes a few minutes and requires the GAIn
environment and access to the GRR.
"""

import gzip
import pandas as pd


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

RUN_EXTENDED_VALIDATION = False

METADATA_FILE = (
    "GSE278576_hippocampus_RNA_seurat_object_filtered_cells_metadata.tsv.gz"
)

OUTPUT_FILE = "zemke2024_annotated_barcode_namespace.csv.gz"

DATASET = "summary/zemke2024Epigenetic"

EXPECTED_ROWS = 295033
EXPECTED_SAMPLES = 40
EXPECTED_SUBCLASSES = 18


# ------------------------------------------------------------
# Build annotated-cell table
# ------------------------------------------------------------

M = pd.read_csv(
    METADATA_FILE,
    sep="\t",
)

required_columns = [
    "bacrode",
    "orig.ident",
    "subclass",
]

missing = [
    column
    for column in required_columns
    if column not in M.columns
]

assert not missing, (
    f"Missing metadata columns: {missing}"
)

# The source metadata uses the column name "bacrode" (sic).
# Preserve the original identifier and make its provenance explicit.
M = M.rename(
    columns={
        "bacrode": "bacrode_GEO",
    }
)

# Sample identity comes directly from the author's orig.ident field.
M["sample"] = M["orig.ident"].astype(str)

# The GRR barcode is the part after the final underscore.
#
# Examples:
#   hc1134_AAACAGCCATTATCCC-1      -> AAACAGCCATTATCCC-1
#   hc11_deep_AAACAGCCATAAGGAC-1 -> AAACAGCCATAAGGAC-1
M["barcode"] = (
    M["bacrode_GEO"]
    .astype(str)
    .str.rsplit("_", n=1)
    .str[-1]
)

OUT = M[
    [
        "sample",
        "bacrode_GEO",
        "barcode",
        "subclass",
    ]
].copy()


# ------------------------------------------------------------
# Fast validation
# ------------------------------------------------------------

for column in OUT.columns:
    assert OUT[column].notna().all(), (
        f"Missing values in {column}"
    )

for column in [
    "sample",
    "bacrode_GEO",
    "barcode",
    "subclass",
]:
    assert (
        OUT[column]
        .astype(str)
        .str.strip()
        .ne("")
        .all()
    ), f"Blank values in {column}"

assert not OUT[
    ["sample", "barcode"]
].duplicated().any(), (
    "Duplicate sample/barcode pairs found"
)

assert len(OUT) == EXPECTED_ROWS, (
    f"Unexpected row count: {len(OUT)}"
)

assert OUT["sample"].nunique() == EXPECTED_SAMPLES, (
    f"Unexpected sample count: {OUT['sample'].nunique()}"
)

assert OUT["subclass"].nunique() == EXPECTED_SUBCLASSES, (
    f"Unexpected subclass count: {OUT['subclass'].nunique()}"
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

OUT.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("Rows:", len(OUT))
print("Samples:", OUT["sample"].nunique())
print("Subclasses:", OUT["subclass"].nunique())
print("Saved:", OUTPUT_FILE)

print("\nFirst rows:")
print(
    OUT.head()
    .to_string(index=False)
)


# ============================================================
# Extended validation
#
# This is not required to generate the resource. It requires
# GAIn/GRR access and checks every annotated barcode against
# both modalities.
#
# Previous validation (2026-09-24):
#
#   RNA+ATAC matrices:
#     found   = 295,033
#     missing = 0
#
#   ATAC fragments:
#     found   = 295,033
#     missing = 0
#
# All 40 GEO sample names were present in both GRR resource
# collections. Thus the same derived barcode can be used for
# the RNA+ATAC matrix and ATAC-fragment resources.
# ============================================================

if RUN_EXTENDED_VALIDATION:

    from gain.genomic_resources.repository_factory import (
        build_genomic_resource_repository,
    )
    from gain.genomic_resources.ann_data_resource import (
        load_ann_data_from_resource,
    )

    print("\nRunning extended validation...")

    grr = build_genomic_resource_repository()

    matrix_found = 0
    fragment_found = 0

    matrix_missing = []
    fragment_missing = []

    # Validate one sample at a time to keep memory use modest.
    for sample, D in OUT.groupby(
        "sample",
        sort=True,
    ):

        expected = set(
            D["barcode"].astype(str)
        )


        # ----------------------------------------------------
        # RNA+ATAC matrix
        # ----------------------------------------------------

        matrix_resource = grr.get_resource(
            f"{DATASET}/"
            f"rna_expression_atac_matrix/{sample}"
        )

        A = load_ann_data_from_resource(
            matrix_resource,
            matrix_free=True,
        )

        matrix_barcodes = set(
            A.obs_names.astype(str)
        )

        missing = expected - matrix_barcodes

        matrix_found += (
            len(expected) - len(missing)
        )

        if missing:
            matrix_missing.extend(
                (sample, barcode)
                for barcode in sorted(missing)
            )


        # ----------------------------------------------------
        # ATAC fragments
        # ----------------------------------------------------

        fragment_resource = grr.get_resource(
            f"{DATASET}/atac_fragments/{sample}"
        )

        filename = (
            fragment_resource
            .get_config()["table"]["filename"]
        )

        found = set()

        with fragment_resource.open_raw_file(
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

                        # No need to scan the rest of the file
                        # once every annotated barcode is found.
                        if len(found) == len(expected):
                            break

        missing = expected - found

        fragment_found += len(found)

        if missing:
            fragment_missing.extend(
                (sample, barcode)
                for barcode in sorted(missing)
            )


    # --------------------------------------------------------
    # Extended-validation results
    # --------------------------------------------------------

    print("\nRNA+ATAC matrix validation:")
    print("Found:", matrix_found)
    print("Missing:", len(matrix_missing))

    print("\nATAC fragment validation:")
    print("Found:", fragment_found)
    print("Missing:", len(fragment_missing))

    assert matrix_found == EXPECTED_ROWS
    assert len(matrix_missing) == 0

    assert fragment_found == EXPECTED_ROWS
    assert len(fragment_missing) == 0

    print("\nExtended validation passed.")

else:
    print("\nExtended validation: OFF")