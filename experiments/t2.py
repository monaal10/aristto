import json
import pandas as pd
import requests
from tqdm import tqdm

headers = {
    "x-api-key": "vd5G9VoPYk3hfCYyPjZR334dvZCumbEF2tkdeQhK",
}
response = requests.get("https://api.semanticscholar.org/datasets/v1/release/latest/dataset/embeddings-specter_v2", headers=headers)
files = response.json().get("files")

with open("files.txt", "w") as f:
    for file in files:
        f.write(f"{file}\n")

"""import pandas as pd
import numpy as np
from tqdm import tqdm

# Load the data
df = pd.read_json("publication.json", lines=True)
df1 = pd.read_csv("journal_quartile_rank.csv")

# Preprocess the data
df['name_lower'] = df['name'].str.lower()
df['alternate_names_lower'] = df['alternate_names'].str.lower()

# Create a dictionary for faster lookup
name_to_id = {}
for _, row in df.iterrows():
    if isinstance(row['name'], str):
        name_to_id[row['name_lower']] = row['id']
    if isinstance(row['alternate_names'], str):
        for alt_name in row['alternate_names_lower'].split(','):
            name_to_id[alt_name.strip()] = row['id']

# Function to find matching ID
def find_matching_id(name):
    if isinstance(name, str) and len(name) > 0:
        name_lower = name.lower()
        return name_to_id.get(name_lower)
    return None

# Apply the function to the DataFrame
tqdm.pandas()
df1['ss_id'] = df1['title'].progress_apply(find_matching_id)

# Save the result
df1.to_csv("jqr.csv", index=False)"""


