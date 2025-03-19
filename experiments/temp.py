import os

import boto3
from azure.storage.blob import BlobServiceClient
# Hardcoded bucket name and folder (prefix)
import pyarrow.parquet as pq
import s3fs

# Hardcoded variables
bucket_name = "aristto-embeddings"
folder_prefix = "paper-text-with-embeddings-parquet"
filename = "part-00000-6464f357-67ad-4cb8-80b6-46fb458ef3e7-c000.snappy.parquet"
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHMGRMPHOZ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
s3_path = f"s3://{bucket_name}/{folder_prefix}/{filename}"

# Create a filesystem object to access S3
fs = s3fs.S3FileSystem(key=os.environ.get('AWS_ACCESS_KEY_ID'),
                      secret=os.environ.get('AWS_SECRET_ACCESS_KEY'))

# Read only the metadata from the Parquet file
metadata = pq.read_metadata(s3_path, filesystem=fs)
num_records = metadata.num_rows

print("Number of records in file:", num_records)


s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

# Use a paginator to iterate through all objects under the given prefix
paginator = s3.get_paginator('list_objects_v2')
page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix)

file_count = 0

for page in page_iterator:
    # 'Contents' key exists if there are objects in this page
    if 'Contents' in page:
        file_count += len(page['Contents'])

print("Total number of files in folder:", file_count)



# Hardcoded variables
connection_string = "DefaultEndpointsProtocol=https;AccountName=openalex;AccountKey=SF4/pZ3WmsOUZst9geosCPq8rGwiFfvJndbNYkj0Mu4ga/P6uYN4vmyYPFsoyOOWi01lYhUN1lZh+AStAuKa8g==;EndpointSuffix=core.windows.net"

 # Folder prefix, ensure it ends with a slash if needed
target_containers = [f"openalex-works-{i}" for i in range(1, 13)]
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
total_file_count = 0
for container_name in target_containers:
    container_client = blob_service_client.get_container_client(container_name)
    # List blobs with the specified folder prefix and count them
    blob_list = container_client.list_blobs()
    file_count = sum(1 for _ in blob_list)
    total_file_count += file_count
print("Total number of files in folder:", file_count)