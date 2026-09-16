from gain.genomic_resources.gene_models import build_gene_models_from_resource_id
from gain.genomic_resources.reference_genome import build_reference_genome_from_resource_id


GM = build_gene_models_from_resource_id("reference/Human/gene_models/refSeq_v20240129").load()
tm = GM.gene_models_by_gene_name("CHD7")[1]

RG = build_reference_genome_from_resource_id("reference/Human/genome/ucsc-hg38").open()
seq = RG.get_sequence(tm.chrom, tm.cds[0], tm.cds[1])
