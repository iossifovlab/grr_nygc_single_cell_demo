gunzip -c hg38.fa.gz | bgzip > hg38.fa.bgz
samtools faidx hg38.fa.bgz
rm hg38.fa.gz