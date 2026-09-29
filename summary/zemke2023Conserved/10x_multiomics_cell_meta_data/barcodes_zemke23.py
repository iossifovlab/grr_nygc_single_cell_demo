"""
Create the Zemke 2023 annotated-cell barcode resource.

Annotated cells and subclass assignments are obtained from the Human,
Macaque, Marmoset, and Mouse GRR RNA-expression matrices. RNA sample names
are compared with the canonical namespace in the sample-description table;
names that differ are explicitly canonicalized, and the table supplies the
corresponding RNA+ATAC and ATAC-fragment resource names.

Set RUN_EXTENDED_VALIDATION = True to verify the annotated barcodes against
the corresponding RNA+ATAC matrices and available ATAC-fragment resources. 

Normal resource generation requires the GAIn environment and access to the GRR. 
Extended validation also requires GAIn/GRR access and takes a few minutes.
"""

import pandas as pd

from gain.genomic_resources.ann_data_resource import (
    load_ann_data_from_resource_id,
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

RUN_EXTENDED_VALIDATION = False

DATASET = "summary/zemke2023Conserved"

SAMPLE_DESCRIPTION_FILE = (
    "sample_description_Ivan260918_zemke23.txt"
)

OUTPUT_FILE = "zemke2023_annotated_barcode_namespace.csv.gz"

SPECIES = [
    "human",
    "macaque",
    "marmoset",
    "mouse",
]

EXPECTED_COUNTS = {
    "human": 40937,
    "macaque": 34773,
    "marmoset": 34310,
    "mouse": 47404,
}

EXPECTED_ROWS = 157424
EXPECTED_SAMPLES = 23
EXPECTED_SUBCLASSES = 20


# ------------------------------------------------------------
# Load sample-description table
# ------------------------------------------------------------

S = pd.read_csv(
    SAMPLE_DESCRIPTION_FILE,
    sep="\t",
)

required_mapping_columns = [
    "sample_id / library_id",
    "rna_expression_atac_matrix",
    "atac_fragments",
]

missing = [
    column
    for column in required_mapping_columns
    if column not in S.columns
]

assert not missing, (
    f"Missing sample-description columns: {missing}"
)

S = S.rename(
    columns={
        "sample_id / library_id": "canonical_sample",
    }
)

assert S["canonical_sample"].notna().all()
assert S["canonical_sample"].is_unique

canonical_samples = set(
    S["canonical_sample"].astype(str)
)


# ------------------------------------------------------------
# Collect annotated cells from RNA-expression matrices
# ------------------------------------------------------------

tables = []

for species in SPECIES:

    A = load_ann_data_from_resource_id(
        f"{DATASET}/rna_expression_matrix/{species}"
    )

    required_obs = [
    "subclass",
]

    assert A.obs.index.name == "cell", (
        f"{species}: expected obs index to be named 'cell', "
        f"found {A.obs.index.name!r}"
    )


    missing = [
        column
        for column in required_obs
        if column not in A.obs.columns
    ]

    assert not missing, (
        f"{species}: missing obs columns: {missing}"
    )

    D = A.obs.reset_index()[
        [
            "cell",
            "subclass",
        ]
    ].copy()

    # Example:
    # M1_donor1_AAACAGCCAACAACAA-1
    # ->
    # M1_donor1 | AAACAGCCAACAACAA-1

    D[
        [
            "rna_expression_matrix",
            "barcode",
        ]
    ] = (
        D["cell"]
        .astype(str)
        .str.rsplit("_", n=1, expand=True)
    )

    D["species"] = species

    tables.append(D)


RNA = pd.concat(
    tables,
    ignore_index=True,
)


# ------------------------------------------------------------
# Canonicalize RNA sample names
#
# Comparison with the sample-description namespace identifies
# the RNA resource names that require conversion.
# ------------------------------------------------------------

rna_samples = set(
    RNA["rna_expression_matrix"].unique()
)

unmatched_rna = (
    rna_samples
    - canonical_samples
)

rna_to_canonical = {
    "mop2c1": "Mop_2C_rep1",
    "mop2c2": "Mop_2C_rep2",
    "mop3c1": "Mop_3C_rep1",
    "mop3c2": "Mop_3C_rep2",
    "mop4b1": "Mop_4B_rep1",
    "mop4b2": "Mop_4B_rep2",
    "mop5d1": "Mop_5D_rep1",
    "mop5d2": "Mop_5D_rep2",
}

# The explicit mapping must account for exactly the RNA names
# that fail direct matching to the canonical namespace.
assert unmatched_rna == set(rna_to_canonical), (
    "Unexpected RNA sample-name differences. "
    f"Observed: {sorted(unmatched_rna)}"
)

# Every target must exist in the canonical namespace.
assert set(
    rna_to_canonical.values()
) <= canonical_samples

# Mapping must be one-to-one.
assert (
    len(set(rna_to_canonical.values()))
    == len(rna_to_canonical)
)

# The unmatched names should occur only in the Mouse resource.
assert set(
    RNA.loc[
        RNA["rna_expression_matrix"].isin(unmatched_rna),
        "species",
    ]
) == {"mouse"}

RNA["canonical_sample"] = (
    RNA["rna_expression_matrix"]
    .replace(rna_to_canonical)
)

unknown_after_mapping = (
    set(RNA["canonical_sample"])
    - canonical_samples
)

assert not unknown_after_mapping, (
    "RNA samples remain unmatched after canonicalization: "
    f"{sorted(unknown_after_mapping)}"
)


# ------------------------------------------------------------
# Add modality-specific resource names
# ------------------------------------------------------------

OUT = RNA.merge(
    S[
        [
            "canonical_sample",
            "rna_expression_atac_matrix",
            "atac_fragments",
        ]
    ],
    on="canonical_sample",
    how="left",
    validate="many_to_one",
)

OUT = OUT[
    [
        "species",
        "canonical_sample",
        "rna_expression_matrix",
        "rna_expression_atac_matrix",
        "atac_fragments",
        "cell",
        "barcode",
        "subclass",
    ]
]


# ------------------------------------------------------------
# Fast validation
# ------------------------------------------------------------

required_output_columns = [
    "species",
    "canonical_sample",
    "rna_expression_matrix",
    "rna_expression_atac_matrix",
    "cell",
    "barcode",
    "subclass",
]

for column in required_output_columns:

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


assert OUT["cell"].is_unique, (
    "cell is not unique"
)

assert not OUT[
    [
        "rna_expression_matrix",
        "barcode",
    ]
].duplicated().any(), (
    "Duplicate RNA sample/barcode pairs found"
)


observed_counts = (
    OUT["species"]
    .value_counts()
    .to_dict()
)

assert observed_counts == EXPECTED_COUNTS, (
    f"Unexpected species counts: {observed_counts}"
)

assert len(OUT) == EXPECTED_ROWS

assert (
    OUT["canonical_sample"].nunique()
    == EXPECTED_SAMPLES
)

assert (
    OUT["subclass"].nunique()
    == EXPECTED_SUBCLASSES
)


# One canonical sample has no ATAC-fragment resource listed
# in the sample-description table.

missing_atac_samples = sorted(
    OUT.loc[
        OUT["atac_fragments"].isna(),
        "canonical_sample",
    ]
    .drop_duplicates()
    .tolist()
)

assert missing_atac_samples == [
    "M1_donor3_rep2"
], (
    "Unexpected samples without ATAC fragments: "
    f"{missing_atac_samples}"
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

OUT.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("Rows:", len(OUT))

print("\nRows by species:")
print(
    OUT["species"]
    .value_counts()
    .to_string()
)

print(
    "\nSamples:",
    OUT["canonical_sample"].nunique(),
)

print(
    "Subclasses:",
    OUT["subclass"].nunique(),
)

print(
    "\nRNA names requiring canonicalization:",
    len(unmatched_rna),
)

for source, target in rna_to_canonical.items():
    print(f"  {source} -> {target}")

print(
    "\nSamples without an ATAC-fragment resource:",
    missing_atac_samples,
)

print("\nSaved:", OUTPUT_FILE)

print("\nFirst rows:")
print(
    OUT.head()
    .to_string(index=False)
)


# ============================================================
# Extended validation
#
# This is not required to generate the resource. It checks all
# annotated barcodes against the corresponding RNA+ATAC matrix
# and, when available, the ATAC-fragment resource.
#
# Previous validation (2026-09-24):
#
#   Annotated cells:    157,424
#   Canonical samples:       23
#   Subclasses:              20
#
#   Comparison of RNA resource names with the sample-description
#   namespace identified eight Mouse names requiring
#   canonicalization; these are checked above on every run.
#
#   All annotated samples have an RNA+ATAC matrix mapping.
#
#   M1_donor3_rep2 has no ATAC-fragment resource listed in the
#   sample-description table.
#
# Resource names are not always identical across modalities, so
# the modality-specific resource-name columns are retained.
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

    matrix_found = 0
    matrix_missing = 0
    matrix_missing_examples = []

    fragment_expected = 0
    fragment_found = 0
    fragment_missing = 0
    fragment_missing_examples = []


    for canonical_sample, D in OUT.groupby(
        "canonical_sample",
        sort=True,
    ):

        expected = set(
            D["barcode"].astype(str)
        )


        # ----------------------------------------------------
        # RNA+ATAC matrix
        # ----------------------------------------------------

        matrix_names = (
            D["rna_expression_atac_matrix"]
            .dropna()
            .unique()
        )

        assert len(matrix_names) == 1

        matrix_name = matrix_names[0]

        matrix_resource = grr.get_resource(
            f"{DATASET}/"
            f"rna_expression_atac_matrix/{matrix_name}"
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

        matrix_missing += len(missing)

        if missing and len(matrix_missing_examples) < 10:
            matrix_missing_examples.extend(
                [
                    (canonical_sample, barcode)
                    for barcode in list(missing)[
                        : 10 - len(matrix_missing_examples)
                    ]
                ]
            )


        # ----------------------------------------------------
        # ATAC fragments
        # ----------------------------------------------------

        fragment_names = (
            D["atac_fragments"]
            .dropna()
            .unique()
        )

        if len(fragment_names) == 0:
            continue

        assert len(fragment_names) == 1

        fragment_name = fragment_names[0]

        fragment_expected += len(expected)

        fragment_resource = grr.get_resource(
            f"{DATASET}/atac_fragments/{fragment_name}"
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

                    barcode = (
                        line.rstrip("\n")
                        .split("\t")[3]
                    )

                    if barcode in expected:
                        found.add(barcode)

                        if len(found) == len(expected):
                            break

        missing = expected - found

        fragment_found += len(found)
        fragment_missing += len(missing)

        if missing and len(fragment_missing_examples) < 10:
            fragment_missing_examples.extend(
                [
                    (canonical_sample, barcode)
                    for barcode in list(missing)[
                        : 10 - len(fragment_missing_examples)
                    ]
                ]
            )


    # --------------------------------------------------------
    # Extended-validation results
    # --------------------------------------------------------

    print("\nRNA+ATAC matrix validation:")
    print("Expected:", EXPECTED_ROWS)
    print("Found:", matrix_found)
    print("Missing:", matrix_missing)

    if matrix_missing_examples:
        print(
            "Missing examples:",
            matrix_missing_examples,
        )


    print("\nATAC fragment validation:")
    print("Expected:", fragment_expected)
    print("Found:", fragment_found)
    print("Missing:", fragment_missing)

    if fragment_missing_examples:
        print(
            "Missing examples:",
            fragment_missing_examples,
        )


    assert matrix_found == EXPECTED_ROWS
    assert matrix_missing == 0

    assert fragment_found == fragment_expected
    assert fragment_missing == 0

    print("\nExtended validation passed.")

else:
    print("\nExtended validation: OFF")