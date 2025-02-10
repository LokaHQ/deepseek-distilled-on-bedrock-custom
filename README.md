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

![arch](https://github.com/user-attachments/assets/3e8021ec-7255-4640-8f35-15a66c67a7ee)

## 🚀 Deployment Methods

### 🖥️ One-click Operations by the Console

This method allows you to deploy DeepSeek models on AWS Bedrock using the AWS Management Console. It is a straightforward approach that involves navigating through the AWS Bedrock service and following the on-screen instructions to deploy the model.

#### Steps

1. **Download the model**: The first step is to download the model you want to deploy (in our case the [DeepSeek R1 Distill Llama 8B model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B) or [DeepSeek R1 Distill Llama 70B model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B)) from HuggingFace on our local machine or directly on a SageMaker Notebook.

   ![deepseek_hf](https://github.com/user-attachments/assets/8907aa32-d7b8-47ef-8b75-f52d1d1a6b6d)
   **The model card for the DeepSeek R1 Distill Llama 8B model on HuggingFace**

   ![deepseek_hf_files](https://github.com/user-attachments/assets/4815d360-f730-48e3-ae13-1d27006d9a98)
   **The files to download for the DeepSeek R1 Distill Llama 8B model on HuggingFace**

    ![image](https://github.com/user-attachments/assets/de884b5d-570e-4dda-b9dd-0ede4bb16a69)
   **The model card for the DeepSeek R1 Distill Llama 70B model on HuggingFace**

   ![image](https://github.com/user-attachments/assets/233e9c83-d521-4888-93d4-48094a944584)
   **The files to download for the DeepSeek R1 Distill Llama 70B model on HuggingFace**

1. **Create an S3 bucket**: The next step is to create an S3 bucket on AWS to store the model files. This bucket will be used to import the model to AWS Bedrock.

   ![aws_console](https://github.com/user-attachments/assets/86519edb-a1ed-4108-96e4-52d2348c5037)
   **Log in to the AWS Management Console.**

   ![s3_bucket](https://github.com/user-attachments/assets/fb5e2898-b90d-4437-8a31-81ab5f209b55)
   **Navigate to the S3 service and click on `Create bucket`**

   ![s3_creation](https://github.com/user-attachments/assets/a1d7ab7e-45d6-49a3-99c9-a24bf94b2f8c)
   **Enter all the necessary details and click on `Create bucket`**

   ![s3_upload](https://github.com/user-attachments/assets/1ed5652b-1d24-49df-b448-3997339848a0)
   **Upload the downloaded model files to this bucket**

2. **Create an IAM role**: The next step is to create an IAM role with the necessary permissions to access the S3 bucket and Bedrock services.

   ![iam_role](https://github.com/user-attachments/assets/6ba77d32-65fd-4d02-81aa-d0351b75161b)
   **Navigate to the IAM service in the AWS Management Console**

   ![iam_create_role](https://github.com/user-attachments/assets/967afae0-9cd0-47e5-93ea-6dd9b447626f)
   **Click on `Create role`**

   ![iam_role_details](https://github.com/user-attachments/assets/aa3d6512-6447-4a1c-87d0-82583e90a53a)
   **Fill in the necessary details and attach the required policies**

3. **Import the model in Bedrock**: The next step is to import the model to AWS Bedrock using the AWS Management Console.

   ![bedrock_import](https://github.com/user-attachments/assets/a9c2fa66-0c39-4be8-a485-56ee5c76ca46)
   **Navigate to the AWS Bedrock service in the AWS Management Console**

   ![bedrock_import_model](https://github.com/user-attachments/assets/fa27bfb5-f2d4-4cb4-aebe-9be568d54dfa)
   **Click on `Import Model`**

   ![bedrock_model_details](https://github.com/user-attachments/assets/5148def2-bd29-4884-94f4-a7617be20bd4)
   **Fill in the necessary details and click on `Import`**

4. **Run Inference**: After the model is imported, you can run inference using the AWS Bedrock service.

    ![inference](https://github.com/user-attachments/assets/f000b4cd-89f5-4306-a848-e40add123c2e)

5. **Delete the Model**: The final step is to delete the model from AWS Bedrock once you are done using it.

    ![delete_model](empty)

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

1. **Deploy the Model**:
    - Run the `./scripts/deploy.py` script to download the model from Hugging Face Hub, upload it to S3, and deploy it to Amazon Bedrock.
    ```bash
    uv run ./scripts/deploy.py --hf_model_id <HF-MODEL-ID> --bucket_name <S3-BUCKET-NAME> --s3_prefix <S3-PREFIX> --local_directory <LOCAL-DIRECTORY> --job_name <CMI-JOB-NAME> --imported_model_name <CMI-MODEL-NAME> --role_arn <IAM-ROLE-ARN> --region_info <AWS-REGION>
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

4. **Delete the Model**:
    - To delete the model from AWS Bedrock, you can run the `./scripts/delete_model.py` script.
    ```bash
    uv run ./scripts/delete.py --model_id <MODEL-ID> --bucket_name <S3-BUCKET-NAME> --s3_prefix <S3-PREFIX> --region_info <AWS-REGION>
    ```

## 📝 Notes

- Ensure that the IAM role specified in `role_arn` has the necessary permissions to access S3 and Bedrock services.
- The `region_info` should be set to a region that supports Amazon Bedrock (currently `us-west-2` and `us-east-1`).
- Adjust the parameters such as `temperature`, `max_tokens`, and `top_p` as needed for your specific use case.
- Bedrock currently works only with DeepSeek Models based on Llama architecture.

## 📂 Repo Structure

```
.
├── benchmark
│   └── benchmark.py
├── scripts
│   ├── delete.py
│   ├── deploy.py
│   └── inference.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```
