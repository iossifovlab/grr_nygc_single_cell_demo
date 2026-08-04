import time
from typing import Generator
import numpy as np
import anndata as ad

fragment_h5ad_file = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/johansen2025Crossspecies/download/BasalGanglia_pre-print_ATAC/human/snapatac2/fe73a2757d8d05fbb09a5d1d9532eda0be0a40fa.h5ad"


fragment_h5ad_file = "/gpfs/commons/groups/iossifov_lab/ylee/GRR/johansen2025Crossspecies/download/BasalGanglia_pre-print_ATAC/marmoset/snaptac2/P0074_3.h5ad"

try:
    FAD
except NameError:
    FAD = ad.read_h5ad(fragment_h5ad_file, backed="r")



refs = FAD.uns["reference_sequences"]
offsets = np.concatenate([[0], np.cumsum(refs.reference_seq_length.values[:-1])])

def iterate_cell_fragmenets_yoon_ha(fad: ad.AnnData, cell_i: int) -> \
        Generator[tuple[int, str, int, int, str, int], None, None]:

    barcode = fad.obs_names[cell_i]
    fp = fad.obsm['fragment_paired']


    for k in range(fp.indptr[cell_i], fp.indptr[cell_i+1]):
        genome_pos = fp.indices[k]
        length = fp.data[k]

        chrom_id = np.searchsorted(offsets, genome_pos, side="right") - 1

        chrom = refs.reference_seq_name.iat[chrom_id]
        start = genome_pos - offsets[chrom_id]
        end = start + length

        yield (chrom_id, chrom, start, end, barcode, 1)


def iterate_cell_fragmenets(fad: ad.AnnData, cell_i: int) -> \
        Generator[tuple[int, str, int, int, str, int], None, None]:

    fp = fad.obsm['fragment_paired']
    refs_lenghts = fad.uns["reference_sequences"].reference_seq_length.to_numpy()
    refs_names = fad.uns["reference_sequences"].reference_seq_name.to_numpy()
    barcode = fad.obs_names[cell_i]

    prev_chrom_i = 0
    prev_chrom_b = 0
    prev_chrom_e = refs_lenghts[prev_chrom_i]

    for k in range(fp.indptr[cell_i], fp.indptr[cell_i+1]):
        gen_pos = fp.indices[k]
        frag_length = fp.data[k]

        while gen_pos > prev_chrom_e:
            prev_chrom_i += 1
            prev_chrom_b = prev_chrom_e
            prev_chrom_e += refs_lenghts[prev_chrom_i]

        chrom_pos_start = gen_pos - prev_chrom_b
        chrom_pos_end = chrom_pos_start + frag_length
        yield (prev_chrom_i, refs_names[prev_chrom_i], chrom_pos_start, chrom_pos_end, barcode, 1)



if __name__ == "__main__":

    for cell_i in range(30):
        ivan_res = list(iterate_cell_fragmenets(FAD, cell_i))
        yoon_ha_res = list(iterate_cell_fragmenets_yoon_ha(FAD, cell_i))

        print(cell_i, len(ivan_res), len(yoon_ha_res), ivan_res == yoon_ha_res)

    t_start = time.time()
    for cell_i in range(10):
        for b in iterate_cell_fragmenets(FAD, cell_i):
            pass # print("Ivan", cell_i, b)
    print("Ivan", time.time() - t_start, "seconds")

    t_start = time.time()
    for cell_i in range(10): # 3050
        for b in iterate_cell_fragmenets_yoon_ha(FAD, cell_i):
            pass # print("Yoon-ha", cell_i, b)
    print("Yoon-ha", time.time() - t_start, "seconds")

    # fp = FAD.obsm['fragment_paired']
    # for cell_i in range(5845):
    #     ss, ee = fp.indptr[cell_i], fp.indptr[cell_i+1]
    #     frag_intervals = list(zip(fp.indices[ss:ee], fp.data[ss:ee]))
    #     df = len(frag_intervals)-len(set(frag_intervals))
    #     print(cell_i, df, len(frag_intervals), len(set(frag_intervals)))
    #     if df > 0:
    #         print("AAAAAAAA")
    #         break
