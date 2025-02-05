"""Benchmark script for measuring latency of the Bedrock model."""

import argparse
import csv
import json
import os
import random
import time
import warnings
from time import perf_counter

import boto3
import numpy as np
from botocore.config import Config
from loguru import logger

warnings.filterwarnings("ignore")


# Prompts for testing
PROMPT_LIST = [
    "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
    "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
    "Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?",
    "Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages should she read?",
    "James writes a 3-page letter to 2 different friends twice a week. How many pages does he write a year?",
    "Mark has a garden with flowers. He planted plants of three different colors in it. Ten of them are yellow, and there are 80% more of those in purple. There are only 25% as many green flowers as there are yellow and purple flowers. How many flowers does Mark have in his garden?",
    "Albert is wondering how much pizza he can eat in one day. He buys 2 large pizzas and 2 small pizzas. A large pizza has 16 slices and a small pizza has 8 slices. If he eats it all, how many pieces does he eat that day?",
    "Ken created a care package to send to his brother, who was away at boarding school. Ken placed a box on a scale, and then he poured into the box enough jelly beans to bring the weight to 2 pounds. Then, he added enough brownies to cause the weight to triple. Next, he added another 2 pounds of jelly beans. And finally, he added enough gummy worms to double the weight once again. What was the final weight of the box of goodies, in pounds?",
    "Alexis is applying for a new job and bought a new set of business clothes to wear to the interview. She went to a department store with a budget of $200 and spent $30 on a button-up shirt, $46 on suit pants, $38 on a suit coat, $11 on socks, and $18 on a belt. She also purchased a pair of shoes, but lost the receipt for them. She has $16 left from her budget. How much did Alexis pay for the shoes?",
    "Tina makes $18.00 an hour. If she works more than 8 hours per shift, she is eligible for overtime, which is paid by your hourly wage + 1/2 your hourly wage. If she works 10 hours every day for 5 days, how much money does she make?",
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Model Testing Script")
    parser.add_argument(
        "--model_id",
        type=str,
        required=True,
        help="Bedrock model ID (The Model ARN)",
    )
    parser.add_argument(
        "--region_info",
        type=str,
        default=os.getenv("region_info"),
        help="AWS region info",
    )
    parser.add_argument(
        "--output_dir", type=str, default="results", help="Output directory for results"
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
        "--cold_start_loops",
        type=int,
        default=2,
        help="Number of cold start loops for a prompt",
    )
    parser.add_argument(
        "--stat_loops",
        type=int,
        default=5,
        help="Number of loops for extracting stats",
    )
    return parser.parse_args()


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


def measure_latency(
    client: boto3.client,
    model_id: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    max_retries: int,
    cold_start_loops: int,
    stat_loops: int,
) -> dict:
    """
    Measure latency of model for a given prompt.

    Args:
        client (boto3.client): Bedrock client
        model_id (str): Bedrock model ID
        prompt (str): Prompt to test
        temperature (float): Controls randomness in generation (0.0-1.0)
        max_tokens (int): Maximum number of tokens to generate
        top_p (float): Nucleus sampling parameter (0.0-1.0)
        max_retries (int): Maximum number of retry attempts
        cold_start_loops (int): Number of cold start loops for a prompt
        stat_loops (int): Number of loops for extracting stats

    Returns:
        dict: Dictionary with latency metrics
    """
    id = random.randint(1, 9999)
    latencies = []
    for _ in range(cold_start_loops):
        _ = generate(
            client, model_id, prompt, temperature, max_tokens, top_p, max_retries
        )
    for _ in range(stat_loops):
        start_time = perf_counter()
        response_body, response_header = generate(
            client, model_id, prompt, temperature, max_tokens, top_p, max_retries
        )
        latency = perf_counter() - start_time
        latencies.append(latency)
    time_avg_ms = 1000 * np.mean(latencies)
    time_std_ms = 1000 * np.std(latencies)
    time_p95_ms = 1000 * np.percentile(latencies, 95)
    time_p50_ms = 1000 * np.percentile(latencies, 50)
    time_min_ms = 1000 * np.min(latencies)
    time_max_ms = 1000 * np.max(latencies)
    return {
        "time_avg_ms": time_avg_ms,
        "time_std_ms": time_std_ms,
        "time_p95_ms": time_p95_ms,
        "time_p50_ms": time_p50_ms,
        "time_min_ms": time_min_ms,
        "time_max_ms": time_max_ms,
        "prompt_length": len(prompt),
        "generation_token_count": response_body["generation_token_count"],
        "prompt_token_count": response_body["prompt_token_count"],
        "input_token_count": response_header["x-amzn-bedrock-input-token-count"],
        "output_token_count": response_header["x-amzn-bedrock-output-token-count"],
        "invocation_latency": response_header["x-amzn-bedrock-invocation-latency"],
    }


def main():
    """Main function to run the benchmark."""
    args = parse_args()

    # Create boto3 client
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=args.region_info,
        config=Config(
            connect_timeout=300,
            read_timeout=300,
            retries={"max_attempts": 3},
        ),
    )

    # Create output directory
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "benchmark.csv")

    # Doing the benchmark
    benchmark_dict = []
    for prompt in PROMPT_LIST:
        res = measure_latency(
            client,
            args.model_id,
            prompt,
            args.temperature,
            args.max_tokens,
            args.top_p,
            args.max_retries,
            args.cold_start_loops,
            args.stat_loops,
        )
        benchmark_dict.append(
            {
                **res,
                "model_id": args.model_id,
                "prompt": prompt,
            }
        )

    # Write results to CSV
    keys = benchmark_dict[0].keys()
    with open(
        output_file,
        "w",
        newline="",
    ) as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(benchmark_dict)


if __name__ == "__main__":
    main()
