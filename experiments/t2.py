from azure.storage.blob import BlobServiceClient
import os

# Connection string for your storage account
connection_string = "DefaultEndpointsProtocol=https;AccountName=openalex;AccountKey=SF4/pZ3WmsOUZst9geosCPq8rGwiFfvJndbNYkj0Mu4ga/P6uYN4vmyYPFsoyOOWi01lYhUN1lZh+AStAuKa8g==;EndpointSuffix=core.windows.net"
source_container = "paper-metadata"
source_prefix = "works/"
target_containers = [f"openalex-works-{i}" for i in range(1, 13)]

# Create a blob service client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get source container client
source_container_client = blob_service_client.get_container_client(source_container)

# List all blobs in the works folder with their sizes
all_blobs = list(source_container_client.list_blobs(name_starts_with=source_prefix))
print(f"Found {len(all_blobs)} blobs to distribute")

# Extract blob sizes and sort blobs from largest to smallest
blob_data = [(blob.name, blob.size) for blob in all_blobs]
blob_data.sort(key=lambda x: x[1], reverse=True)  # Sort descending by size

# Initialize container size tracking
container_assignments = {container: [] for container in target_containers}
container_sizes = {container: 0 for container in target_containers}

# Distribute blobs using a greedy algorithm (assign to container with least total size)
for blob_name, blob_size in blob_data:
    target_container = min(container_sizes, key=container_sizes.get)  # Pick the least loaded container
    container_assignments[target_container].append(blob_name)
    container_sizes[target_container] += blob_size  # Update total size of this container

# Now copy the blobs to their assigned containers
for container, blobs in container_assignments.items():
    target_container_client = blob_service_client.get_container_client(container)
    print(f"Copying {len(blobs)} blobs ({container_sizes[container]} bytes) to {container}")

    for blob_name in blobs:
        source_blob = source_container_client.get_blob_client(blob_name)

        # Remove the "works/" prefix for the destination blob
        dest_name = blob_name[len(source_prefix):] if blob_name.startswith(source_prefix) else blob_name

        # Get a blob client for the destination
        target_blob = target_container_client.get_blob_client(dest_name)

        # Start copy operation
        target_blob.start_copy_from_url(source_blob.url)
        print(f"Started copy: {blob_name} -> {container}/{dest_name}")

print("Copy operations initiated. Check the Azure portal for progress.")
