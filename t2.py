import numpy as np
import faiss
import os
from datasets import load_dataset
import pandas as pd
import random
nprobe = 16
D = 384
def create_faiss_index(memmap_file, index_file, batch_size=100000):
    # Load the memmap file
    embeddings = np.memmap(memmap_file, dtype=np.float16, mode='r').reshape(-1, D)

    # Get the number of vectors and dimensionality
    num_vectors = embeddings.shape[0]
    dim = embeddings.shape[1]

    print(f"Creating Faiss index for {num_vectors} vectors of dimension {dim}")
    nlist = 16384
    m = 48  # number of subquantizers
    k = 4
    # Create a Faiss index
    #quantizer = faiss.IndexFlatL2(D)  # this remains the same
    #index = faiss.IndexIVFPQ(quantizer, D, nlist, m, 8) # Enable on-disk index
    #index.ivf_on_disk_read = True
    #index.train(embeddings[:batch_size])
    #faiss.write_index(index, f'/Volumes/SEAGATE BAC/abstracts-search/partial-indices/index_initial.faiss')
    # Add vectors to the index in batches
    for i in range(29700000, num_vectors, batch_size):
        index = faiss.read_index(index_file)
        #index = faiss.IndexIVFFlat(dim, 4)
        idxs_chunk = np.arange(i, min(i + batch_size, len(embeddings)))
        end = min(i + batch_size, num_vectors)
        batch = embeddings[i:end].astype(np.float32)  # Faiss requires float32
        index.add(batch)
        print(f"Added vectors {i} to {end}")
        faiss.write_index(index, f'/Volumes/SEAGATE BAC/abstracts-search/partial-indices/index_{idxs_chunk[-1]:03d}.faiss')


works_ids_path = '/Volumes/SEAGATE BAC/abstracts-search/abstracts-embeddings/openalex_ids.txt'


#ds = load_dataset("colonelwatch/abstracts-embeddings")

# Usage
memmap_file = '/Volumes/SEAGATE BAC/abstracts-search/abstracts-embeddings/embeddings.memmap'
index_file = '/Volumes/SEAGATE BAC/abstracts-search/partial-indices/index_initial.faiss'


create_faiss_index(memmap_file, index_file)