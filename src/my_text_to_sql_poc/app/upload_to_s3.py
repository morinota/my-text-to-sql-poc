from pathlib import Path

import boto3
from loguru import logger


def upload_to_s3(file_path: Path, bucket_name: str, s3_key: str):
    """
    Upload a file to an S3 bucket.

    Args:
        file_path (Path): Local path to the file to upload.
        bucket_name (str): Name of the S3 bucket.
        s3_key (str): Key (path) in the S3 bucket where the file will be stored.
    """
    s3 = boto3.client("s3")
    try:
        s3.upload_file(str(file_path), bucket_name, s3_key)
        logger.info(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logger.error(f"Failed to upload {file_path} to S3: {e}")


if __name__ == "__main__":
    bucket_name = "staging-newspicks-datalake-mart"
    base_s3_path = "tmp/text2sql_poc/"

    files_to_upload = [
        Path("data/table_metadata_store.duckdb"),
        Path("data/sample_query_store.duckdb"),
    ]

    for file_path in files_to_upload:
        if file_path.exists():
            s3_key = base_s3_path + file_path.name
            upload_to_s3(file_path, bucket_name, s3_key)
        else:
            logger.warning(f"File not found: {file_path}")
