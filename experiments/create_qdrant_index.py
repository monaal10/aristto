"""
Main Pipeline Orchestrator
"""
import boto3
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio
import aiohttp
import gzip
import json
from typing import List, Dict, Generator, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, QuantizationConfig, ScalarQuantization
import tempfile
from pathlib import Path
import shutil
import pandas as pd
import pyarrow.parquet as pq

os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHMGRMPHOZ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Author:
    def __init__(self, author_id: str, name: str):
        self.author_id = author_id
        self.name = name

    @classmethod
    def from_dict(cls, data: Dict) -> 'Author':
        return cls(
            author_id=data.get('authorId', ''),
            name=data.get('name', '')
        )

    def to_dict(self) -> Dict:
        return {
            'authorId': self.author_id,
            'name': self.name
        }

class PaperMetadata:
    def __init__(self, corpus_id: str, authors: List[Author], jqr: Optional[float], publication_year: Optional[int]):
        self.corpus_id = corpus_id
        self.authors = authors
        self.jqr = jqr
        self.publication_year = publication_year

    @classmethod
    def from_dict(cls, data: Dict) -> 'PaperMetadata':
        authors = [Author.from_dict(author) for author in data.get('authors', [])]
        return cls(
            corpus_id=data.get('corpusid', ''),
            authors=authors,
            jqr=data.get('jqr'),
            publication_year=data.get('publication_year')
        )

    def to_dict(self) -> Dict:
        return {
            'corpus_id': self.corpus_id,
            'authors': [author.to_dict() for author in self.authors],
            'author_ids': [author.author_id for author in self.authors],
            'author_names': [author.name for author in self.authors],
            'jqr': self.jqr,
            'publication_year': self.publication_year
        }

class PipelineConfig:
    def __init__(self):
        self.s3_bucket = "aristto-embeddings"
        self.download_concurrency = 150
        self.process_concurrency = 32
        self.batch_size = 1000
        self.vector_size = 512  # Adjust based on your vectors
        self.collection_name = 'research_papers'

class DownloadWorker:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.temp_dir = tempfile.mkdtemp()
        self.download_semaphore = asyncio.Semaphore(self.config.download_concurrency)

    async def download_and_process_file(self, url: str, file_index: int) -> str:
        """Download, extract, and cleanup in one go"""
        gz_path = os.path.join(self.temp_dir, f"{file_index}.gz")
        json_path = os.path.join(self.temp_dir, f"{file_index}.json")

        try:
            # Download with semaphore
            async with self.download_semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url.strip()) as response:
                        with open(gz_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)

            # Extract and delete gz file
            with gzip.open(gz_path, 'rt') as gz_file, open(json_path, 'w') as json_file:
                for line in gz_file:
                    json_file.write(line)

            os.remove(gz_path)
            return json_path

        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            if os.path.exists(gz_path):
                os.remove(gz_path)
            return None

class QdrantManager:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.client = QdrantClient("localhost", port=6333)

    def initialize_collection(self):
        """Initialize Qdrant collection with binary quantization"""
        self.client.recreate_collection(
            collection_name=self.config.collection_name,
            vectors_config=VectorParams(
                size=self.config.vector_size,
                distance=Distance.COSINE,
                quantization_config=ScalarQuantization(
                    type="binary",
                    always_ram=True
                )
            )
        )

    def upload_batch(self, batch: List[Dict]):
        """Upload a batch of vectors to Qdrant"""
        points = [
            {
                'id': idx,
                'vector': item['vector'],
                'payload': item['metadata']
            } for idx, item in enumerate(batch)
        ]
        self.client.upload_points(
            collection_name=self.config.collection_name,
            points=points
        )

    def backup_to_s3(self):
        """Backup Qdrant collection to S3"""
        snapshot_path = self.client.create_snapshot(
            collection_name=self.config.collection_name
        )

        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        s3.upload_file(
            snapshot_path,
            self.config.s3_bucket,
            f"qdrant_snapshots/{self.config.collection_name}/latest.snapshot"
        )

class MetadataManager:
    def __init__(self, metadata_file: str):
        self.metadata_file = metadata_file
        self._metadata_cache = {}
        self._parquet_table = None
        self._load_parquet_table()

    def _load_parquet_table(self):
        """Load the Parquet file into memory"""
        self._parquet_table = pq.read_table(self.metadata_file)
        # Convert to pandas for easier filtering
        self._df = self._parquet_table.to_pandas()
        # Set corpus_id as index for faster lookups
        self._df.set_index('corpusid', inplace=True)

    def load_metadata_batch(self, corpus_ids: List[str]) -> Dict:
        """Load metadata for specific corpus IDs"""
        # Filter the DataFrame for the requested corpus IDs
        batch_df = self._df.loc[self._df.index.intersection(corpus_ids)]

        # Convert the filtered data to the expected format
        result = {}
        for corpus_id, row in batch_df.iterrows():
            # Parse the authors list (assuming it's stored as a string representation of JSON)
            try:
                authors = json.loads(row['authors']) if isinstance(row['authors'], str) else row['authors']
            except (json.JSONDecodeError, TypeError):
                authors = []

            metadata = {
                'corpus_id': corpus_id,
                'authors': authors,
                'author_ids': [author.get('authorId', '') for author in authors],
                'author_names': [author.get('name', '') for author in authors],
                'jqr': row.get('jqr'),
                'publication_year': row.get('publication_year')
            }
            result[corpus_id] = metadata

        return result

async def main():
    config = PipelineConfig()

    # Initialize components
    downloader = DownloadWorker(config)
    qdrant_manager = QdrantManager(config)
    metadata_manager = MetadataManager('metadata.parquet')  # Updated to use parquet file

    # Initialize Qdrant collection
    qdrant_manager.initialize_collection()

    # Process URLs in batches
    with open('files.txt', 'r') as f:
        urls = f.readlines()

    # Download and process files concurrently
    tasks = [
        downloader.download_and_process_file(url, idx)
        for idx, url in enumerate(urls)
    ]
    json_files = await asyncio.gather(*tasks)
    json_files = [f for f in json_files if f]  # Remove None values

    # Process JSON files and upload to Qdrant
    def process_json_file(json_path: str) -> Generator[Dict, None, None]:
        corpus_ids = []
        vectors = []

        with open(json_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                corpus_ids.append(data['corpusid'])
                vectors.append(data['vector'])

                if len(corpus_ids) >= config.batch_size:
                    metadata = metadata_manager.load_metadata_batch(corpus_ids)
                    yield from [
                        {'vector': v, 'metadata': metadata.get(cid, {})}
                        for v, cid in zip(vectors, corpus_ids)
                    ]
                    corpus_ids = []
                    vectors = []

        # Process remaining items
        if corpus_ids:
            metadata = metadata_manager.load_metadata_batch(corpus_ids)
            yield from [
                {'vector': v, 'metadata': metadata.get(cid, {})}
                for v, cid in zip(vectors, corpus_ids)
            ]

    # Process files in parallel using ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=config.process_concurrency) as executor:
        for json_path in json_files:
            for batch in executor.map(lambda x: list(process_json_file(x)), [json_path]):
                qdrant_manager.upload_batch(batch)
            # Delete JSON file after processing
            os.remove(json_path)

    # Backup Qdrant collection to S3
    qdrant_manager.backup_to_s3()

    # Cleanup temporary directory
    shutil.rmtree(downloader.temp_dir)

if __name__ == "__main__":
    asyncio.run(main())