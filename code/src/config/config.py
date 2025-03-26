import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = BASE_DIR / "models"

# Define data file paths
DATA_FILES = {
    "transactions": DATA_DIR / "Account_Statement.csv",
    "credit_card_transactions": DATA_DIR / "credit_card_transactions.csv",
    "social_media": DATA_DIR / "social_media_posts.csv",
    "new_social_media": DATA_DIR / "new_social_media_posts.csv",
    "kyc": DATA_DIR / "KYC_Details.csv",
    "emails": DATA_DIR / "emails_to_wells_fargo.csv",
    "receiver_categories": DATA_DIR / "Receiver_vs_Category.csv",
    "available_credit_cards": DATA_DIR / "Wells_Fargo_Credit_Card_Details.csv",
    "available_loans": DATA_DIR / "Wells_Fargo_Loan_Details.csv",
    "credit_card_list": DATA_DIR / "credit_card_list.csv"
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

# Model paths
LLM_MODEL_PATH = MODELS_DIR / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Output settings
OUTPUT_SETTINGS = {
    "insights_file": "insights.txt",
    "email_draft_file": "email_draft.txt",
    "date_format": "%Y-%m-%d"
}

# Create necessary directories
for directory in [DATA_DIR, OUTPUT_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True) 