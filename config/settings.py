"""
Configuration settings for the PipelineBovespa project.
"""

# AWS Configuration
AWS_REGION = "us-east-1"  # Change to your preferred region

# S3 Configuration
S3_BUCKET_RAW = "bovespa-raw-data"  # Bucket for raw data
S3_BUCKET_REFINED = "bovespa-refined-data"  # Bucket for refined data
S3_PREFIX_RAW = "raw/"  # Prefix for raw data
S3_PREFIX_REFINED = "refined/"  # Prefix for refined data

# Glue Configuration
GLUE_DATABASE = "bovespa_db"  # Glue catalog database name
GLUE_JOB_NAME = "bovespa-etl-job"  # Glue job name

# Data Configuration
LOCAL_DATA_DIR = "data"  # Local directory for data storage during development
RAW_DATA_DIR = f"{LOCAL_DATA_DIR}/raw"  # Raw data directory
REFINED_DATA_DIR = f"{LOCAL_DATA_DIR}/refined"  # Refined data directory

# B3 Website Configuration
B3_URL = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
