from gain.genomic_resources.repository_factory import \
    build_genomic_resource_repository


grr = build_genomic_resource_repository()
# # In zemke2024 this is "individual_id"


# for ri, r in enumerate(grr.search_resources(resource_query="summary/zemke2024Epigenetic/atac_fragments/*")):
#     ind_id = r.get_labels()["individual_id"]
#     print(f'add_labels.py "{{sample_id: {ind_id}}}"  ../{r.resource_id}')


# # Not available in liu.. . But we can assign sample_id by using the last segment of the resrouce_id.
# for ri, r in enumerate(grr.search_resources(resource_query="summary/liu2026Multiomics/atac_fragments/*")):
#     sample_id = r.resource_id.split("/")[-1]
#     print(f'add_labels.py "{{sample_id: {sample_id}}}"  ../{r.resource_id}')


# Not avialable in johansen. But can be assigned using the "constant" suffix
# for the "cell" score. Can easily/cheaply be obtained from the histogram-cell.json
import sys
from gain.genomic_resources.genomic_scores import \
    build_fragment_score_from_resource_id
import pandas as pd
from collections import defaultdict, Counter

cell_meta = pd.read_csv("/Users/iiossifov/work/nygc_ai_initiative/barcode_resources/johansen2025Crossspecies/johansen2025_annotated_barcode_namespace.csv.gz")

bc_samples = defaultdict(lambda: defaultdict(list))
for t in cell_meta.itertuples(index=False):
    bc_samples[t.species.lower()][t.barcode].append(t.sample_id)

bc_samples = {sp: dict(spd) for sp, spd in bc_samples.items()}

for ri, r in enumerate(grr.search_resources(resource_query="summary/johansen2025Crossspecies/atac_fragments/*")):
    # print(r.resource_id, r.get_type(), r.get_labels())
    print(ri, r.resource_id, file=sys.stderr)

    sc = build_fragment_score_from_resource_id(r.resource_id)

    cell_hist = sc.get_score_histogram("cell", truncated=True)
    # print(cell_hist.to_dict()["values"])
    cells = list(cell_hist.to_dict()["values"].keys())


    sample_ids = {cell.split("-")[1] for cell in cells}
    assert len(sample_ids) == 1
    sample_id, = sample_ids

    species = r.resource_id.split("/")[-2]
    sample_counts = Counter([sm for cell in cells if cell in bc_samples[species] for sm in bc_samples[species][cell]])
    samples2 = [sm for sm, cnt in sample_counts.items() if cnt == len(cells)]

    if species == "human":
        assert len(samples2) == 1
        sample_id2, = samples2
        assert sample_id == sample_id2
    elif species == "marmoset":
        if r.resource_id.endswith(".h5ad"):
            assert len(samples2) == 1
            sample_id2, = samples2
            assert sample_id == sample_id2
        else:
            assert len(samples2) in [0, 1]
            if len(samples2) == 1:
                sample_id2, = samples2
                assert sample_id == sample_id2

    elif species == "macaque":
        assert len(samples2) == 1
        sample_id, = samples2
    else:
        assert False
    # assert len(samples2) == 1
    # sample_id2, = samples2

    # assert sample_id == sample_id2 or species == 'macaque'

    print("\t", sample_id, samples2, file=sys.stderr)
    print(f'add_labels.py "{{sample_id: {sample_id}}}"  ../{r.resource_id}')
    # if ri > 5:
    #     break
