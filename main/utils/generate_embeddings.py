import os
import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Tuple


class TextDataset(Dataset):
    def __init__(self, texts: List[str], tokenizer, max_length: int = 512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx]

    def collate_fn(self, batch):
        return self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )


def load_model() -> Tuple[AutoTokenizer, AutoModel, torch.device]:
    """Load the embedding model with mixed precision support"""
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model_name = "avsolatorio/NoInstruct-small-Embedding-v0"
    print(f"Loading model '{model_name}' on device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModel.from_pretrained(model_name).to(device)

    # Enable mixed precision
    if device.type == 'cuda':
        model = model.half()  # Convert to FP16

    model.eval()
    return tokenizer, model, device


def get_embeddings_dataloader(
        texts: List[str],
        tokenizer: AutoTokenizer,
        model: AutoModel,
        device: torch.device,
        batch_size: int = 512,
) -> np.ndarray:
    """Generate embeddings using DataLoader for efficient batching"""
    dataset = TextDataset(texts, tokenizer)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        collate_fn=dataset.collate_fn,
        pin_memory=True if device.type == 'cuda' else False
    )

    all_embeddings = []

    with torch.no_grad(), torch.cuda.amp.autocast(enabled=device.type == 'cuda'):
        for batch in tqdm(dataloader, desc="Processing batches"):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            all_embeddings.append(embeddings.cpu().float().numpy())

    return np.concatenate(all_embeddings)


def get_output_path(parquet_file: str, output_folder: str) -> str:
    """Generate the output JSON path for a given parquet file"""
    return os.path.join(
        output_folder,
        os.path.basename(parquet_file).replace('.parquet', '.json')
    )


def process_file(
        parquet_file: str,
        output_folder: str,
        tokenizer: AutoTokenizer,
        model: AutoModel,
        device: torch.device,
        batch_size: int = 512
) -> None:
    """Process a single parquet file if the output doesn't already exist or is 0 bytes"""
    output_path = get_output_path(parquet_file, output_folder)

    # Check if output file already exists and is non-empty
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"\nSkipping {parquet_file} - output already exists at {output_path}")
        return

    print(f"\nProcessing: {parquet_file}")

    # Load entire parquet file
    df = pd.read_parquet(parquet_file)

    if 'text' not in df.columns:
        print(f"Column 'text' not found in {parquet_file}. Skipping file.")
        return

    texts = df['text'].tolist()
    print(f"Processing {len(texts):,} texts")

    # Generate embeddings in batches
    embeddings = get_embeddings_dataloader(
        texts, tokenizer, model, device, batch_size=batch_size
    )

    # Save results
    df['embeddings'] = embeddings.tolist()
    df.to_json(output_path, orient='records', lines=True)

    # Clear memory
    del df, embeddings
    torch.cuda.empty_cache()


def main():
    local_folder = "parquet_data_final"
    output_folder = "paper_text_embeddings"
    os.makedirs(output_folder, exist_ok=True)

    parquet_files = [
        os.path.join(local_folder, f)
        for f in os.listdir(local_folder)
        if f.endswith(".parquet")
    ]

    if not parquet_files:
        print(f"No parquet files found in folder: {local_folder}")
        return

    print(f"Found {len(parquet_files)} parquet file(s)")

    # Identify files that need processing:
    # Process if the output file doesn't exist OR if it exists but is 0 bytes.
    files_to_process = [
        f for f in parquet_files
        if (not os.path.exists(get_output_path(f, output_folder))) or
           (os.path.exists(get_output_path(f, output_folder)) and os.path.getsize(get_output_path(f, output_folder)) == 0)
    ]
    print(f"Files requiring processing: {len(files_to_process)} out of {len(parquet_files)}")

    if not files_to_process:
        print("All files have been processed already. Nothing to do.")
        return

    # Load model
    tokenizer, model, device = load_model()

    # Process files
    for parquet_file in tqdm(files_to_process, desc="Processing files"):
        try:
            process_file(parquet_file, output_folder, tokenizer, model, device)
        except Exception as e:
            print(f"Error processing file {parquet_file}: {str(e)}")
            continue

    print("Processing completed.")


if __name__ == "__main__":
    main()
