import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Data file names
DATA_FILES = {
    "transactions": "account_statement.csv",
    "credit_card": "credit_card_transactions.csv",
    "kyc": "KYC_Details.csv",
    "social_media": "social_media_posts.csv",
    "emails": "emails_to_wells_fargo.csv"
}

# Analysis settings
ANALYSIS_SETTINGS = {
    "spending_clusters": 3,
    "high_value_threshold": 0.9,  # 90th percentile for high-value transactions
    "subscription_categories": ["streaming", "subscription", "membership"],
    "savings_optimization": {
        "subscription": 0.2,  # 20% potential optimization
        "impulse_purchases": 0.15  # 15% potential reduction
    }
}

# LLM settings
LLM_SETTINGS = {
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 1000,
    "email_max_tokens": 800
}

# Output settings
OUTPUT_SETTINGS = {
    "insights_file": "insights.txt",
    "email_draft_file": "email_draft.txt",
    "date_format": "%Y-%m-%d"
}

# Create necessary directories
for directory in [DATA_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True) 