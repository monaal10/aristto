import faiss
import os
import numpy as np
# Directory where the FAISS index files are stored
index_folder = "/Volumes/SEAGATE BAC/abstracts-search/partial-indices/"
merged_index = faiss.read_index("/Volumes/SEAGATE BAC/abstracts-search/partial-indices/combined.faiss", faiss.IO_FLAG_MMAP)
index_files = [os.path.join(index_folder, f) for f in os.listdir(index_folder) if f.endswith('.faiss') and not f.startswith('.')]
query_vector = np.random.random((1, 384)).astype('float32')
k = 5  # Number of nearest neighbors to retrieve
D, I = merged_index.search(query_vector, k)
# Load the first index
print(f"Loading index: {index_files[0]}")


# Initialize an ID offset value to avoid overlap in IDs

# Merge the rest of the indexes into the first one
for idx_file in index_files[1:]:
    print(f"Merging index: {idx_file}")

    # Read the index to merge
    index_to_merge = faiss.read_index(idx_file)

    # Merge the index with an ID offset to avoid collision
    faiss.merge_into(merged_index, index_to_merge, shift_ids=True)


# Save the merged index to a new file
output_file = "/Volumes/SEAGATE BAC/abstracts-search/partial-indices/combined.faiss"
faiss.write_index(merged_index, output_file)
print(f"Saved merged index to {output_file}")
