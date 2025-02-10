"""Script for deleting the model from Amazon Bedrock and optionally from S3"""

import argparse
import os

import boto3
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def delete_model(model_id: str, region_info: str) -> None:
    """
    Delete model from Amazon Bedrock

    Args:
        model_id (str): Bedrock model ID
        region_info (str): AWS region info

    Returns:
        None

    Raises:
        Exception: Error deleting model
    """
    try:
        logger.info(f"Deleting model from Amazon Bedrock: {model_id}")
        bedrock = boto3.client("bedrock", region_name=region_info)
        bedrock.delete_imported_model(
            modelIdentifier=model_id,
        )
        logger.info(f"Model deleted successfully: {model_id}")
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        raise


def delete_s3_objects(bucket_name: str, s3_prefix: str, region_info: str) -> None:
    """
    Delete objects from S3 bucket

    Args:
        bucket_name (str): S3 bucket name
        s3_prefix (str): S3 prefix
        region_info (str): AWS region info

    Returns:
        None

    Raises:
        Exception: Error deleting objects from S3
    """
    try:
        logger.info(f"Deleting objects from S3 bucket: {bucket_name}")
        s3 = boto3.client("s3", region_name=region_info)
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

        delete_us = dict(Objects=[])
        for item in pages.search("Contents"):
            delete_us["Objects"].append(dict(Key=item["Key"]))

            # Flush once AWS limit reached
            if len(delete_us["Objects"]) >= 1000:
                s3.delete_objects(Bucket=bucket_name, Delete=delete_us)
                delete_us = dict(Objects=[])

        # Flush remaining items
        if delete_us["Objects"]:
            s3.delete_objects(Bucket=bucket_name, Delete=delete_us)

        logger.info(f"Objects deleted successfully from S3 bucket: {bucket_name}")
    except Exception as e:
        logger.error(f"Error deleting objects from S3: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete model and optionally S3 objects")
    parser.add_argument("--model_id", help="Bedrock model ID (The Model ARN)", required=True)
    parser.add_argument("--bucket_name", help="S3 bucket name")
    parser.add_argument("--s3_prefix", help="S3 prefix")
    parser.add_argument("--region_info", default=os.getenv("region_info"), help="AWS region info")

    args = parser.parse_args()

    delete_model(model_id=args.model_id, region_info=args.region_info)

    if args.bucket_name and args.s3_prefix:
        delete_s3_objects(
            bucket_name=args.bucket_name,
            s3_prefix=args.s3_prefix,
            region_info=args.region_info,
        )
