"""Inference script for the Bedrock model"""

import argparse
import json
import os
import time

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def generate(
    client: boto3.client,
    model_id: str,
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    top_p: float = 0.9,
    max_retries: int = 10,
):
    """
    Generate response using the Bedrock model

    Args:
        client (boto3.client): Bedrock client
        model_id (str): Bedrock model ID
        prompt (str): Prompt for the model
        temperature (float): Controls randomness in generation (0.0-1.0)
        max_tokens (int): Maximum number of tokens to generate
        top_p (float): Nucleus sampling parameter (0.0-1.0)
        max_retries (int): Maximum number of retry attempts

    Returns:
        dict: Response body
        dict: Response headers

    Exceptions:
        Exception: Failed to get response after maximum retries
    """

    logger.info("Generating response using the model")

    attempt = 0
    while attempt < max_retries:
        try:
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(
                    {
                        "prompt": prompt,
                        "temperature": temperature,
                        "max_gen_len": max_tokens,
                        "top_p": top_p,
                    }
                ),
                accept="application/json",
                contentType="application/json",
            )

            result_body = json.loads(response["body"].read().decode("utf-8"))
            result_headers = response["ResponseMetadata"]["HTTPHeaders"]
            logger.info("Response generated successfully")
            return result_body, result_headers

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            attempt += 1
            if attempt < max_retries:
                time.sleep(30)
    raise Exception("Failed to get response after maximum retries")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inference script for the Bedrock model"
    )
    parser.add_argument(
        "--model_id", help="Bedrock model ID (The Model ARN)", required=True
    )
    parser.add_argument(
        "--hf_model_id",
        default=os.getenv("hf_model_id"),
        help="Hugging Face model ID",
    )
    parser.add_argument(
        "--region_info", default=os.getenv("region_info"), help="AWS region info"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Controls randomness in generation (0.0-1.0)",
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=4096,
        help="Maximum number of tokens to generate",
    )
    parser.add_argument(
        "--top_p", type=float, default=0.9, help="Nucleus sampling parameter (0.0-1.0)"
    )
    parser.add_argument(
        "--max_retries", type=int, default=10, help="Maximum number of retry attempts"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="""Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. 
    How many clips did Natalia sell altogether in April and May?""",
        help="Prompt for the model",
    )

    args = parser.parse_args()

    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=args.region_info,
        config=Config(
            connect_timeout=300,
            read_timeout=300,
            retries={"max_attempts": 3},
        ),
    )

    response_body, response_header = generate(
        client=client,
        model_id=args.model_id,
        prompt=args.prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        max_retries=args.max_retries,
    )

    logger.info(f"Generated text: {response_body['generation']}")
    logger.info(f"Generation token count: {response_body['generation_token_count']}")
    logger.info(f"Prompt token count: {response_body['prompt_token_count']}")
    logger.info(
        f"Input token count: {response_header['x-amzn-bedrock-input-token-count']}"
    )
    logger.info(
        f"Output token count: {response_header['x-amzn-bedrock-output-token-count']}"
    )
    logger.info(
        f"Invocation latency: {response_header['x-amzn-bedrock-invocation-latency']}"
    )
