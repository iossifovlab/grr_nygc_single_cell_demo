"""
Create the Johansen 2025 annotated-cell barcode resource.

The Human, Macaque, and Marmoset comprehensive RNA-expression resources
are used as the source of annotated cells. Cell barcode, sample identity,
and hierarchical cell-type annotations are taken directly from AnnData.obs,
and the AnnData index is retained as the full cell_label.

Set RUN_EXTENDED_VALIDATION = True to rerun the slower taxonomy
and ATAC-resource validation described at the end of the script. 

Normal resource generation requires the GAIn environment and access to the GRR. 
Extended validation also requires GAIn/GRR access and takes a few minutes.
"""

import gzip
import pandas as pd

from gain.genomic_resources.repository_factory import (
    build_genomic_resource_repository,
)
from gain.genomic_resources.ann_data_resource import (
    load_ann_data_from_resource,
)
from gain.genomic_resources.data_frame_resource import (
    load_data_frame_from_resource_id,
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

RUN_EXTENDED_VALIDATION = False

DATASET = "summary/johansen2025Crossspecies"

OUTPUT_FILE = "johansen2025_annotated_barcode_namespace.csv.gz"

SPECIES = ["Human", "Macaque", "Marmoset"]

EXPECTED_COUNTS = {
    "Human": 1034819,
    "Macaque": 548281,
    "Marmoset": 313033,
}


# ------------------------------------------------------------
# Build annotated-cell table
# ------------------------------------------------------------

grr = build_genomic_resource_repository()

tables = []

for species in SPECIES:

    resource = grr.get_resource(
        f"{DATASET}/comprehensive_rna_expression_matrix/{species}"
    )

    # Avoid loading the large expression matrix; only obs is needed.
    A = load_ann_data_from_resource(
        resource,
        matrix_free=True,
    )

    required_obs = [
        "cell_barcode",
        "barcoded_cell_sample_label",
        "Neighborhood",
        "Class",
        "Subclass",
        "Group",
        "Cluster",
    ]

    missing = [
        column
        for column in required_obs
        if column not in A.obs.columns
    ]

    assert not missing, (
        f"{species}: missing obs columns: {missing}"
    )

    D = A.obs[required_obs].copy()

    # AnnData index is the full cell identifier used across modalities.
    D["cell_label"] = D.index.astype(str)
    D["species"] = species

    D = D.rename(
        columns={
            "barcoded_cell_sample_label": "sample",
        }
    )

    tables.append(D)


OUT = pd.concat(
    tables,
    ignore_index=True,
)

OUT = OUT[
    [
        "species",
        "sample",
        "cell_label",
        "cell_barcode",
        "Neighborhood",
        "Class",
        "Subclass",
        "Group",
        "Cluster",
    ]
]


# ------------------------------------------------------------
# Fast validation
# ------------------------------------------------------------

for column in OUT.columns:
    assert OUT[column].notna().all(), (
        f"Missing values in {column}"
    )

assert OUT["cell_label"].is_unique, (
    "cell_label is not unique"
)

observed_counts = (
    OUT["species"]
    .value_counts()
    .to_dict()
)

assert observed_counts == EXPECTED_COUNTS, (
    f"Unexpected species counts: {observed_counts}"
)

assert len(OUT) == 1896133


# ------------------------------------------------------------
# Derive ATAC-fragment cell identifier
#
# Human and Marmoset fragments use full cell_label values.
# Macaque fragments use cell_barcode with a trailing "-1".
# atac_cell_id is left blank when the expected ATAC fragment
# resource is not present in the GRR.
# ------------------------------------------------------------

cell_metadata_for_atac = load_data_frame_from_resource_id(
    f"{DATASET}/rna_expression_metadata/"
    "HMBA-10xMultiome-BG-Aligned/20260415/"
    "cell_metadata"
)[
    [
        "cell_label",
        "barcoded_cell_sample_label",
        "alignment_job_id",
    ]
].copy()

assert cell_metadata_for_atac["cell_label"].is_unique
assert len(cell_metadata_for_atac) == len(OUT)

atac_link = OUT[
    [
        "species",
        "cell_label",
        "cell_barcode",
    ]
].merge(
    cell_metadata_for_atac,
    on="cell_label",
    how="inner",
    validate="one_to_one",
)

assert len(atac_link) == len(OUT)

atac_link["atac_resource_name"] = (
    atac_link["alignment_job_id"].astype(str)
)

marmoset = atac_link["species"].eq("Marmoset")

atac_link.loc[
    marmoset,
    "atac_resource_name",
] = atac_link.loc[
    marmoset,
    "barcoded_cell_sample_label",
].astype(str)


def output_atac_resource_exists(
    species,
    resource_name,
):

    resource_id = (
        f"{DATASET}/atac_fragments/"
        f"{species.lower()}/{resource_name}"
    )

    try:
        grr.get_resource(resource_id)
        return True
    except Exception:
        return False


atac_resources = atac_link[
    [
        "species",
        "atac_resource_name",
    ]
].drop_duplicates()

atac_resources["atac_resource_exists"] = [
    output_atac_resource_exists(
        species,
        resource_name,
    )
    for species, resource_name in zip(
        atac_resources["species"],
        atac_resources["atac_resource_name"],
    )
]

atac_link = atac_link.merge(
    atac_resources,
    on=[
        "species",
        "atac_resource_name",
    ],
    how="left",
    validate="many_to_one",
)

atac_link["atac_cell_id"] = pd.NA

available = atac_link["atac_resource_exists"]

human_or_marmoset = (
    atac_link["species"].isin(
        ["Human", "Marmoset"]
    )
    & available
)

atac_link.loc[
    human_or_marmoset,
    "atac_cell_id",
] = atac_link.loc[
    human_or_marmoset,
    "cell_label",
]

macaque = (
    atac_link["species"].eq("Macaque")
    & available
)

atac_link.loc[
    macaque,
    "atac_cell_id",
] = (
    atac_link.loc[
        macaque,
        "cell_barcode",
    ]
    + "-1"
)

assert (
    atac_link.loc[
        available,
        "atac_cell_id",
    ]
    .notna()
    .all()
)

assert (
    atac_link.loc[
        ~available,
        "atac_cell_id",
    ]
    .isna()
    .all()
)

atac_id_by_label = (
    atac_link
    .set_index("cell_label")["atac_cell_id"]
)

OUT.insert(
    4,
    "atac_cell_id",
    OUT["cell_label"].map(atac_id_by_label),
)

print(
    "\nATAC cell IDs:",
    OUT["atac_cell_id"].notna().sum(),
    "present,",
    OUT["atac_cell_id"].isna().sum(),
    "blank",
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
    "\nSamples / libraries:",
    OUT["sample"].nunique(),
)

print("\nUnique clusters by species:")
print(
    OUT.groupby("species")["Cluster"]
    .nunique()
    .to_string()
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
# This is not required to generate the resource.
# It loads additional metadata and checks the provenance of the
# annotations and ATAC barcode namespace, so it is slower.
#
# Previous validation (2026-09-24):
#
#   Taxonomy:
#     1,896,133 cells matched exactly between the comprehensive
#     matrices and cell_to_cluster_membership.
#
#   ATAC resource availability:
#     Human       1,034,819 / 1,034,819
#     Macaque       548,281 /   548,281
#     Marmoset      294,480 /   313,033
#
#     18,553 Marmoset cells belong to samples for which no ATAC
#     fragment resource is present in this GRR.
#
#   ATAC fragments use the full cell_label identifier rather
#   than only the bare 16-base cell_barcode.
# ============================================================

if RUN_EXTENDED_VALIDATION:

    print("\nRunning extended validation...")


    # --------------------------------------------------------
    # 1. Compare with the independent taxonomy membership table
    # --------------------------------------------------------

    taxonomy = load_data_frame_from_resource_id(
        f"{DATASET}/rna_expression_metadata/"
        "HMBA-BG-taxonomy-CCN20250428/20250630/"
        "cell_to_cluster_membership"
    )[
        [
            "cell_label",
            "cluster_alias",
        ]
    ].copy()

    assert taxonomy["cell_label"].is_unique
    assert len(taxonomy) == len(OUT)

    taxonomy_check = OUT[
        [
            "cell_label",
            "Cluster",
        ]
    ].merge(
        taxonomy,
        on="cell_label",
        how="inner",
        validate="one_to_one",
    )

    assert len(taxonomy_check) == len(OUT)

    assert (
        taxonomy_check["Cluster"]
        == taxonomy_check["cluster_alias"]
    ).all()

    print(
        "Taxonomy validation:",
        len(taxonomy_check),
        "cells matched",
    )


    # --------------------------------------------------------
    # 2. Determine whether an ATAC resource exists for each cell
    #
    # Human and Macaque ATAC resources are named by
    # alignment_job_id.
    #
    # Marmoset ATAC resources are named by
    # barcoded_cell_sample_label.
    # --------------------------------------------------------

    cell_metadata = load_data_frame_from_resource_id(
        f"{DATASET}/rna_expression_metadata/"
        "HMBA-10xMultiome-BG-Aligned/20260415/"
        "cell_metadata"
    )[
        [
            "cell_label",
            "barcoded_cell_sample_label",
            "alignment_job_id",
        ]
    ].copy()

    assert cell_metadata["cell_label"].is_unique
    assert len(cell_metadata) == len(OUT)

    validation = OUT[
        [
            "species",
            "cell_label",
        ]
    ].merge(
        cell_metadata,
        on="cell_label",
        how="inner",
        validate="one_to_one",
    )

    assert len(validation) == len(OUT)

    validation["atac_resource_name"] = (
        validation["alignment_job_id"]
        .astype(str)
    )

    marmoset = validation["species"].eq("Marmoset")

    validation.loc[
        marmoset,
        "atac_resource_name",
    ] = validation.loc[
        marmoset,
        "barcoded_cell_sample_label",
    ].astype(str)


    def resource_exists(resource_id):
        try:
            grr.get_resource(resource_id)
            return True
        except Exception:
            return False


    resources = validation[
        [
            "species",
            "atac_resource_name",
        ]
    ].drop_duplicates()

    resources["atac_resource_exists"] = [
        resource_exists(
            f"{DATASET}/atac_fragments/"
            f"{species.lower()}/{resource_name}"
        )
        for species, resource_name in zip(
            resources["species"],
            resources["atac_resource_name"],
        )
    ]

    validation = validation.merge(
        resources,
        on=[
            "species",
            "atac_resource_name",
        ],
        how="left",
        validate="many_to_one",
    )

    atac_summary = (
        validation
        .groupby("species")["atac_resource_exists"]
        .agg(
            annotated_cells="size",
            cells_with_atac="sum",
        )
    )

    atac_summary["cells_without_atac"] = (
        atac_summary["annotated_cells"]
        - atac_summary["cells_with_atac"]
    )

    print("\nATAC resource availability:")
    print(atac_summary.to_string())


    # --------------------------------------------------------
    # 3. Confirm representative ATAC resources contain
    #    annotated cells using the expected barcode namespace.
    #
    # Fragment files may contain cells that are not present in
    # the annotated-cell table, so each file is scanned until
    # an expected annotated cell is encountered.
    #
    # For the representative Human and Marmoset resources,
    # fragment identifiers are compared with full cell_label
    # values. For Macaque, the trailing "-1" is removed and
    # the fragment identifier is compared with cell_barcode.
    # --------------------------------------------------------

    representative_atac_resources = {
        "Human": (
            f"{DATASET}/atac_fragments/human/"
            "03a248f86e5097210b0343b1c22edb588a592d41"
        ),
        "Macaque": (
            f"{DATASET}/atac_fragments/macaque/"
            "02345d0e5642fa4ede7968c3f7c77b68b3b64498"
        ),
        "Marmoset": (
            f"{DATASET}/atac_fragments/marmoset/"
            "P0005_2"
        ),
    }

    cell_barcode_by_label = (
        OUT.set_index("cell_label")["cell_barcode"]
    )


    def find_annotated_fragment_cell(
        species,
        resource_id,
    ):

        resource_name = resource_id.rsplit("/", 1)[-1]

        expected_cells = validation.loc[
            (
                validation["species"].eq(species)
                & validation["atac_resource_name"].eq(
                    resource_name
                )
            ),
            "cell_label",
        ]

        assert len(expected_cells) > 0, (
            f"{species}: no annotated cells mapped to "
            f"{resource_name}"
        )

        if species == "Macaque":
            expected = set(
                expected_cells.map(
                    cell_barcode_by_label
                )
            )
        else:
            expected = set(expected_cells)

        resource = grr.get_resource(resource_id)

        filename = (
            resource
            .get_config()["table"]["filename"]
        )

        with resource.open_raw_file(
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

                    fragment_cell = (
                        line.rstrip("\n")
                        .split("\t")[3]
                    )

                    if species == "Macaque":
                        candidate = (
                            fragment_cell
                            .removesuffix("-1")
                        )
                    else:
                        candidate = fragment_cell

                    if candidate in expected:
                        return fragment_cell

        return None


    print("\nRepresentative ATAC barcode checks:")

    for species, resource_id in (
        representative_atac_resources.items()
    ):

        matched_cell = (
            find_annotated_fragment_cell(
                species,
                resource_id,
            )
        )

        assert matched_cell is not None, (
            f"{species}: no annotated cell found in "
            f"{resource_id}"
        )

        print(
            species,
            "->",
            matched_cell,
            "matched",
        )


    print("\nExtended validation passed.")

else:

    print("\nExtended validation: OFF")
