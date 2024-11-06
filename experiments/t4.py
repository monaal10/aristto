from io import StringIO

import boto3
from botocore.exceptions import NoCredentialsError
import os
import pandas as pd
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHMGRMPHOZ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket.

    :param file_name: File to upload
    :param bucket: Bucket name
    :param object_name: S3 object name. If not specified, file_name is used.
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    try:
        s3.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} successfully uploaded to {bucket}/{object_name}")
        return True
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
        return False
    except NoCredentialsError:
        print("Credentials not available.")
        return False

# Specify your file and bucket name
file_name = 'files.txt'
bucket_name = 'aristto-embeddings'

# Call the function to upload
upload_file_to_s3(file_name, bucket_name)
"""s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
# Get the S3 object
s3_object = s3.get_object(Bucket=bucket_name, Key='final-output/part-00000-0c3d05c9-c5a1-4e44-8858-7ec02e611b0c-c000.csv')

# Read the content of the file in memory
csv_content = s3_object['Body'].read().decode('utf-8')

# Use StringIO to convert the string data into a file-like object for pandas
csv_buffer = StringIO(csv_content)

# Read the CSV in chunks and print the first 5 rows
chunk_size = 100  # Adjust this size based on your memory capacity

# Reading the first chunk to access the first 5 rows
csv_reader = pd.read_csv(csv_buffer, chunksize=chunk_size)

# Get the first chunk
first_chunk = next(csv_reader)

# Print the first 5 rows
print(first_chunk)"""