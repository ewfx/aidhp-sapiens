from pathlib import Path

# Define base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Define data file paths
DATA_FILES = {
    "transactions": DATA_DIR / "Account_Statement.csv",
    "credit_card_transactions": DATA_DIR / "credit_card_transactions.csv",
    "social_media": DATA_DIR / "social_media_posts.csv",
    "kyc": DATA_DIR / "KYC_Details.csv",
    "emails": DATA_DIR / "emails_to_wells_fargo.csv",
    "receiver_categories": DATA_DIR / "Receiver_vs_Category.csv",
    "credit_cards": DATA_DIR / "Wells_Fargo_Credit_Card_Details.csv",
    "loans": DATA_DIR / "Wells_Fargo_Loan_Details.csv",
    "credit_card_list": DATA_DIR / "credit_card_list.csv"
}

# Model paths
LLM_MODEL_PATH = MODELS_DIR / "mistral-7b-instruct-v0.2.Q4_K_M.gguf" 