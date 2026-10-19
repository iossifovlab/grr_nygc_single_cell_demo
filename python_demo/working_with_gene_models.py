import gain.grr as grr

GM = grr.build_gene_models_from_resource_id("reference/Human/gene_models/refSeq_v20240129").load()
tm = GM.gene_models_by_gene_name("CHD7")[1]

RG = grr.build_reference_genome_from_resource_id("reference/Human/genome/ucsc-hg38").open()
seq = RG.get_sequence(tm.chrom, tm.cds[0], tm.cds[1])
