
from gain.genomic_resources.genomic_scores import \
    build_score_from_resource_id
from gain.genomic_resources.reference_genome import \
    build_reference_genome_from_resource_id


resources_to_test = [
    # "summary/zemke2023Conserved/atac_fragments/M1_donor1_deep2",
    # "summary/zemke2023Conserved/atac_fragments/M1_Dheni_deep2",
    # "summary/zemke2023Conserved/atac_fragments/M1_meadow_deep",
    # "summary/zemke2023Conserved/atac_fragments/2C_rep1_deep",
    # "summary/zemke2023Conserved/pseudobulk_atac/human_m1/ASC",
    # "summary/zemke2023Conserved/pseudobulk_atac/macaque_m1/ASC",
    # "summary/zemke2023Conserved/pseudobulk_atac/marmoset_m1/ASC",
    # "summary/zemke2023Conserved/pseudobulk_atac/mouse_mop/ASC",

    "summary/johansen2025Crossspecies/atac_fragments/human/03a248f86e5097210b0343b1c22edb588a592d41",
    "summary/johansen2025Crossspecies/atac_fragments/macaque/02345d0e5642fa4ede7968c3f7c77b68b3b64498",
    "summary/johansen2025Crossspecies/atac_fragments/marmoset/P0005_2",

    "summary/johansen2025Crossspecies/pseudobulk_atac/human/AMY-SLEA-BNST_D1_GABA/bigwig",
    "summary/johansen2025Crossspecies/pseudobulk_atac/macaque/AMY-SLEA-BNST_D1_GABA/bigwig",
    "summary/johansen2025Crossspecies/pseudobulk_atac/marmoset/AMY-SLEA-BNST_GABA/bigwig"


]

for res_id in resources_to_test:
    sc = build_score_from_resource_id(res_id).open()
    labels = sc.resource.get_labels()
    ref_id = labels['reference_genome']
    ref = build_reference_genome_from_resource_id(ref_id)
    score_chroms_set = set(sc.get_all_chromosomes())
    ref_chroms_set = set(ref.chromosomes)
    print("Resource: ", res_id)
    print("Genome: ", labels['reference_genome'])
    print("Species: ", labels['species'])
    print("IS OK: ", len(score_chroms_set - ref_chroms_set) == 0)
    print(f"   {len(score_chroms_set - ref_chroms_set)=} "
          f"{len(score_chroms_set)=}, {len(ref_chroms_set)=},")

    if len(score_chroms_set - ref_chroms_set):
        print("\tlongest score chroms:",
              sorted(score_chroms_set,
                     key=lambda x: -sc.table.get_chromosome_length(x))[:5])
        print("\tlongest genome chroms:",
              [y[0] for y in list(sorted(ref.get_all_chrom_lengths().items(),
                                  key=lambda x: -x[1]))[:5]])
    print("\n")
