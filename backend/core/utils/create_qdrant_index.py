import uuid
import boto3
import numpy as np
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, QuantizationConfig, ScalarQuantization, ScalarType
from tqdm import tqdm
import os


def inspect_jsonl_file(s3_client, bucket_name, file_key):
    """Inspect the data types of columns in a JSONL file."""
    print(f"\nInspecting file {file_key} from S3...")
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    lines = response['Body'].iter_lines()

    # Inspect the first line
    first_line = json.loads(next(lines))
    print("\nColumn data types:")
    for key, value in first_line.items():
        print(f"{key}: {type(value).__name__}")

    # Print a sample of the embeddings
    if 'embeddings' in first_line:
        print("\nSample of embeddings:")
        print(first_line['embeddings'])
        print("Type of first embedding:", type(first_line['embeddings']))
        if isinstance(first_line['embeddings'], (list, np.ndarray)):
            print("Length of first embedding:", len(first_line['embeddings']))


def download_jsonl_files(bucket_name, prefix):
    """List JSONL files from S3 bucket."""
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    files = []

    print("Scanning S3 bucket for JSONL files...")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get('Contents', []):
            files.append(obj['Key'])

    return files


def process_jsonl_file_streaming(s3_client, bucket_name, file_key, batch_size=1000):
    """Process a single JSONL file directly from S3 and yield batches of records."""
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    lines = response['Body'].iter_lines()

    batch = []
    for line in lines:
        try:
            record = json.loads(line.decode('utf-8'))
            batch.append(record)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON line: {e}")
            continue

        if len(batch) >= batch_size:
            # Prepare batch data
            embeddings = np.array([record['embeddings'] for record in batch])
            payload = [{k: v for k, v in record.items() if k != 'embeddings'}
                       for record in batch]

            yield embeddings, payload
            batch = []

    if batch:
        embeddings = np.array([record['embeddings'] for record in batch])
        payload = [{k: v for k, v in record.items() if k != 'embeddings'}
                   for record in batch]
        yield embeddings, payload


def create_qdrant_collection(client, collection_name):
    """Create a new Qdrant collection with HNSW and binary quantization."""
    print(f"Creating Qdrant collection {collection_name}...")

    # Delete the collection if it already exists
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"Old collection {collection_name} deleted.")
    except Exception as e:
        print(f"Error deleting collection {collection_name}: {e}")

    # Create a new collection
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
            on_disk=True
        ),
        quantization_config=models.ScalarQuantization(
            scalar=models.ScalarQuantizationConfig(
                type="int8"
            )
        ),
        hnsw_config=models.HnswConfigDiff(
            m=16,
            ef_construct=200,
            full_scan_threshold=10000,
            on_disk=True
        ),
        on_disk_payload=True
    )


def main():
    # Configuration
    BUCKET_NAME = 'aristto-embeddings'
    PREFIX = 'final-data-with-embeddings'
    COLLECTION_NAME = 'embeddings_collection'
    BATCH_SIZE = 1000
    QDRANT_HOST = "localhost"
    QDRANT_PORT = 6333

    # Initialize clients
    s3_client = boto3.client('s3')
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Create collection (deletes old collection and creates new one)
    create_qdrant_collection(qdrant_client, COLLECTION_NAME)

    # Get list of files to process
    file_list = download_jsonl_files(BUCKET_NAME, PREFIX)
    print(f"Found {len(file_list)} JSONL files to process")

    # Inspect first file for debugging
    inspect_jsonl_file(s3_client, BUCKET_NAME, file_list[0])

    # Process files
    total_processed = 0
    for file_key in tqdm(file_list, desc="Processing files", unit='file'):
        try:
            # Start a per-file progress bar
            file_tqdm = tqdm(desc=f"Processing {file_key}", total=1, leave=False, unit="file")

            for embeddings, payload in process_jsonl_file_streaming(
                    s3_client, bucket_name=BUCKET_NAME, file_key=file_key, batch_size=BATCH_SIZE):
                # Upload batch to Qdrant (no tqdm here for batch level)
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=models.Batch(
                        ids=[str(uuid.uuid4()) for i in range(len(embeddings))],
                        vectors=embeddings.tolist(),
                        payloads=payload
                    )
                )

                total_processed += len(embeddings)

            # Update and close the file-level progress bar
            file_tqdm.update(1)
            file_tqdm.close()

        except Exception as e:
            print(f"\nError processing file {file_key}: {str(e)}")
            continue

    print(f"\nFinished processing all files. Total vectors processed: {total_processed}")


if __name__ == "__main__":
    main()
