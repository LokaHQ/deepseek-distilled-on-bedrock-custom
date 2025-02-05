"""Script for deployment of the model to Amazon Bedrock"""

import argparse
import os
import time

import boto3
from dotenv import load_dotenv
from huggingface_hub import snapshot_download
from loguru import logger

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
load_dotenv()


def download_model(repo_id: str, download_path: str) -> None:
    """
    Download model from Hugging Face Hub using snapshot_download

    Args:
        repo_id (str): Hugging Face Hub repo ID
        download_path (str): Path to download the model

    Returns:
        None

    Raises:
        Exception: Error downloading model
    """
    try:
        logger.info(f"Downloading model from Hugging Face Hub: {repo_id}")
        if os.path.exists(download_path) and os.listdir(download_path):
            logger.info(f"Model already downloaded at: {download_path}")
            return
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        snapshot_download(repo_id=repo_id, local_dir=download_path)
        logger.info(f"Model downloaded successfully to: {download_path}")
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        raise


def upload_model_s3(
    download_path: str, bucket_name: str, s3_prefix: str, region_info: str
) -> None:
    """
    Upload model to S3 bucket

    Args:
        download_path (str): Path to download the model
        bucket_name (str): S3 bucket name
        s3_prefix (str): S3 prefix
        region_info (str): AWS region info

    Returns:
        None

    Raises:
        Exception: Error uploading model to S3
    """
    try:
        logger.info(f"Uploading model to S3 bucket: {bucket_name}")
        s3 = boto3.client("s3", region_name=region_info)

        # Check if the model is already uploaded
        for root, _, files in os.walk(download_path):
            for file in files:
                s3_key = os.path.join(s3_prefix, file)
                try:
                    s3.head_object(Bucket=bucket_name, Key=s3_key)
                    logger.info(f"Model file already exists in S3: {s3_key}")
                except s3.exceptions.ClientError:
                    s3.upload_file(
                        os.path.join(root, file),
                        bucket_name,
                        s3_key,
                    )
                    logger.info(f"Uploaded model file to S3: {s3_key}")

        logger.info(f"Model uploaded successfully to S3 bucket: {bucket_name}")
    except Exception as e:
        logger.error(f"Error uploading model to S3: {e}")
        raise


def deploy_model(
    bucket_name: str,
    s3_prefix: str,
    region_info: str,
    role_arn: str,
    job_name: str,
    imported_model_name: str,
) -> None:
    """
    Deploy model to Amazon Bedrock Imported Model

    Args:
        bucket_name (str): S3 bucket name
        s3_prefix (str): S3 prefix
        region_info (str): AWS region info
        role_arn (str): IAM role ARN
        job_name (str): CMI job name
        imported_model_name (str): CMI model name

    Returns:
        None

    Raises:
        Exception: Error deploying model
    """
    try:
        logger.info(f"Deploying model to Amazon Bedrock: {imported_model_name}")
        bedrock = boto3.client("bedrock", region_name=region_info)
        s3_uri = f"s3://{bucket_name}/{s3_prefix}/"
        response = bedrock.create_model_import_job(
            jobName=job_name,
            importedModelName=imported_model_name,
            roleArn=role_arn,
            modelDataSource={"s3DataSource": {"s3Uri": s3_uri}},
        )

        job_arn = response["jobArn"]

        logger.info(f"Model deployment job created: {job_arn}")

        while True:
            response = bedrock.get_model_import_job(jobIdentifier=job_arn)
            status = response["status"].upper()
            logger.info(f"Status: {status}")

            if status in ["COMPLETED", "FAILED"]:
                break

            time.sleep(30)

        # Get the model ID
        model_id = response.get("importedModelArn", "Model ID not available")

        logger.info(f"Waiting for 5 minutes for cold start")
        time.sleep(300)
        logger.info(f"Model ID: {model_id}")
    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and deploy model")
    parser.add_argument(
        "--hf_model_id",
        default=os.getenv("hf_model_id"),
        help="Hugging Face model ID",
    )
    parser.add_argument(
        "--bucket_name", default=os.getenv("bucket_name"), help="S3 bucket name"
    )
    parser.add_argument("--s3_prefix", default=os.getenv("s3_prefix"), help="S3 prefix")
    parser.add_argument(
        "--local_directory",
        default=os.getenv("local_directory"),
        help="Local directory to store downloaded model",
    )
    parser.add_argument(
        "--job_name", default=os.getenv("job_name"), help="CMI job name"
    )
    parser.add_argument(
        "--imported_model_name",
        default=os.getenv("imported_model_name"),
        help="CMI model name",
    )
    parser.add_argument(
        "--role_arn", default=os.getenv("role_arn"), help="IAM role ARN"
    )
    parser.add_argument(
        "--region_info", default=os.getenv("region_info"), help="AWS region info"
    )

    args = parser.parse_args()

    download_model(repo_id=args.hf_model_id, download_path=args.local_directory)
    upload_model_s3(
        download_path=args.local_directory,
        bucket_name=args.bucket_name,
        s3_prefix=args.s3_prefix,
        region_info=args.region_info,
    )
    deploy_model(
        bucket_name=args.bucket_name,
        s3_prefix=args.s3_prefix,
        region_info=args.region_info,
        role_arn=args.role_arn,
        job_name=args.job_name,
        imported_model_name=args.imported_model_name,
    )
