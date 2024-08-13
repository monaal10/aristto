import os
import boto3
from botocore.exceptions import NoCredentialsError
import logging

os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODU27KHAM2XYDGK'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_to_s3():
    folder_path = os.getcwd()

    s3 = boto3.client('s3')
    bucket = "paper-figures"
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]

    for png_file in png_files:
        try:
            full_path = os.path.join(folder_path, png_file)
            s3.upload_file(full_path, bucket, png_file)
            print(f"Upload Successful: {full_path} to {bucket}/{png_file}")
            os.remove(full_path)
            logger.info(f"Deleted local file: {png_file}")
        except FileNotFoundError:
            raise(f"The file was not found")
        except NoCredentialsError:
            raise ("Credentials not available")
    return png_files