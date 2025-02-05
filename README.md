# deepseek-distilled-on-bedrock-custom 🪨

A code repository for deploying distilled versions of DeepSeek-R1 on Bedrock as Custom Models (or any other Open Source Model)

## 📋 Prerequisites

1. **🔑 AWS Account**: Ensure you have an AWS account with the necessary permissions.
2. **🔐 IAM Role**: Create an IAM role with sufficient permissions to access S3 and Bedrock services.
3. **🪣 S3 Bucket**: Create an S3 bucket to store the model files.
4. **[uv](https://docs.astral.sh/uv/)**: An extremely fast Python package and project manager for the code approach.
5. **[git-lfs](https://git-lfs.github.com/)**: Git extension for versioning large files for the code approach of downloading the model.
6. **AWS CLI**: Ensure your AWS account is configured locally (access key and secret key or use `aws-vault`).

## 🏗️ Architecture

![️Arch](./assets/arch.png)

## 🚀 Deployment Methods

### 🖥️ One-click Operations by the Console

This method allows you to deploy DeepSeek models on AWS Bedrock using the AWS Management Console. It is a straightforward approach that involves navigating through the AWS Bedrock service and following the on-screen instructions to deploy the model.

#### Steps

1. **Download the model**: The first step is to download the model you want to deploy (in our case the [DeepSeek R1 Distill Llama 8B model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B)) from HuggingFace on our local machine or directly on a SageMaker Notebook.

   ![Model Card](./assets/deepseek_hf.png)
   **The model card for the DeepSeek R1 Distill Llama 8B model on HuggingFace**

   ![Files for Download](./assets/deepseek_hf_files.png)
   **The files to download for the DeepSeek R1 Distill Llama 8B model on HuggingFace**

2. **Create an S3 bucket**: The next step is to create an S3 bucket on AWS to store the model files. This bucket will be used to import the model to AWS Bedrock.

   ![Console AWS](./assets/aws_console.png)
   **Log in to the AWS Management Console.**

   ![S3 Bucket](./assets/s3_bucket.png)
   **Navigate to the S3 service and click on `Create bucket`**

   ![Create Bucket](./assets/s3_creation.png)
   **Enter all the necessary details and click on `Create bucket`**

   ![Upload Model Bucket](./assets/s3_upload.png)
   **Upload the downloaded model files to this bucket**

3. **Create an IAM role**: The next step is to create an IAM role with the necessary permissions to access the S3 bucket and Bedrock services.

   ![IAM Role](./assets/iam_role.png)
   **Navigate to the IAM service in the AWS Management Console**

   ![Create Role](./assets/iam_create_role.png)
   **Click on `Create role`**

   ![Role Details](./assets/iam_role_details.png)
   **Fill in the necessary details and attach the required policies**

4. **Import the model in Bedrock**: The final step is to import the model to AWS Bedrock using the AWS Management Console.

   ![Bedrock Import](./assets/bedrock_import.png)
   **Navigate to the AWS Bedrock service in the AWS Management Console**

   ![Import Model](./assets/bedrock_import_model.png)
   **Click on `Import Model`**

   ![Model Details](./assets/bedrock_model_details.png)
   **Fill in the necessary details and click on `Import`**

After following these steps, the model will be imported to AWS Bedrock and you can start using it for inference.

![Inference](./assets/inference.png)

### 👨🏻‍💻 Code Approach with boto3

This method involves using code to deploy the DeepSeek models(or any other Open Source Model) on AWS Bedrock. 

#### Environment Setup

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    ```

2. **Install `uv`**:
    ```bash
    pip install uv
    ```

3. **Install `git-lfs`**:
    ```bash
    sudo apt-get install git-lfs
    ```

4. **Sync the Environment**:
    ```bash
    uv sync
    ```

5. **Configure AWS CLI or AWS Vault**:
    - Ensure your AWS account is configured locally using AWS CLI or AWS Vault.
    ```bash
    aws configure
    ```
    - Alternatively, you can use AWS Vault for managing your credentials securely.
    ```bash
    aws-vault add <profile-name>
    ```

6. **Create an S3 Bucket (if not available)**:
    - If you do not have an S3 bucket, you can create one using the AWS CLI.
    ```bash
    aws s3 mb s3://<YOUR-PREDEFINED-S3-BUCKET-TO-HOST-IMPORT-MODEL>
    ```

7. **Configure Environment Variables**:
    - Copy the example environment file and update it with your specific values.
    ```bash
    cp .env.example .env
    ```
    - Edit the `.env` file with your preferred text editor and fill in the required values:
    ```bash
    bucket_name = "<YOUR-PREDEFINED-S3-BUCKET-TO-HOST-IMPORT-MODEL>"
    s3_prefix = "<S3-PREFIX>"
    local_directory = "<LOCAL-FOLDER-TO-STORE-DOWNLOADED-MODEL>"
    hf_model_id = "<HF-MODEL-ID>"
    job_name = '<CMI-JOB-NAME>'
    imported_model_name = '<CMI-MODEL-NAME>'
    role_arn = '<IAM-ROLE-ARN>'
    region_info = 'us-west-2'
    ```

#### Deployment Steps & Testing

1. **Download and Deploy the Model**:
    - Run the `./scripts/download_model_n_deploy.py` script to download the model from Hugging Face Hub, upload it to S3, and deploy it to Amazon Bedrock.
    ```bash
    uv run ./scripts/download_model_n_deploy.py --hf_model_id <HF-MODEL-ID> --bucket_name <S3-BUCKET-NAME> --s3_prefix <S3-PREFIX> --local_directory <LOCAL-DIRECTORY> --job_name <CMI-JOB-NAME> --imported_model_name <CMI-MODEL-NAME> --role_arn <IAM-ROLE-ARN> --region_info <AWS-REGION>
    ```

2. **Run Inference**:
    - After the model is deployed, you can run inference using the `./scripts/inference.py` script.
    ```bash
    uv run ./scripts/inference.py --model_id <MODEL-ID> --hf_model_id <HF-MODEL-ID> --region_info <AWS-REGION> --temperature 0.3 --max_tokens 4096 --top_p 0.9 --max_retries 10 --prompt "<PROMPT>"
    ```

3. **Run Benchmarking**:
    - You can also run benchmarking using the `./benchmark/benchmark.py` script.
    ```bash
    uv run ./benchmark/benchmark.py --model_id <MODEL-ID> --region_info <AWS-REGION> --temperature 0.3 --max_tokens 4096 --top_p 0.9 --max_retries 10 --cold_start_loops 2 --stat_loops 5 --output_dir <OUTPUT-DIR>
    ```

## 📝 Notes

- Ensure that the IAM role specified in `role_arn` has the necessary permissions to access S3 and Bedrock services.
- The `region_info` should be set to a region that supports Amazon Bedrock (currently `us-west-2` and `us-east-1`).
- Adjust the parameters such as `temperature`, `max_tokens`, and `top_p` as needed for your specific use case.
- Bedrock currently works only with DeepSeek Models based on Llama architecture.

## 📂 Directory Structure

```
.
├── benchmark
│   └── benchmark.py
├── scripts
│   ├── download_model_n_deploy.py
│   └── inference.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```
