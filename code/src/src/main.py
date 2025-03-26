import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from src.ai.llm_interaction import LLMInteraction
from src.utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

def load_data() -> Dict[str, Any]:
    """Load all necessary data for the application."""
    logger.info("Loading application data")
    try:
        # Load credit cards data
        credit_cards_path = Path("data/credit_cards.csv")
        logger.debug(f"Loading credit cards data from {credit_cards_path}")
        credit_cards_df = pd.read_csv(credit_cards_path)
        credit_cards = credit_cards_df.to_dict('records')
        logger.info(f"Loaded {len(credit_cards)} credit cards")

        # Load spending data
        spending_path = Path("data/spending_data.json")
        logger.debug(f"Loading spending data from {spending_path}")
        with open(spending_path, 'r') as f:
            spending_data = json.load(f)
        logger.info("Loaded spending data")

        # Load KYC details
        kyc_path = Path("data/kyc_details.json")
        logger.debug(f"Loading KYC details from {kyc_path}")
        with open(kyc_path, 'r') as f:
            kyc_details = json.load(f)
        logger.info("Loaded KYC details")

        return {
            'credit_cards': credit_cards,
            'spending_data': spending_data,
            'kyc_details': kyc_details
        }
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def main():
    """Main application entry point."""
    logger.info("Starting application")
    try:
        # Initialize LLM
        logger.info("Initializing LLM interaction")
        llm = LLMInteraction()

        # Load data
        data = load_data()

        # Example usage
        logger.info("Processing example query")
        query = "What credit cards would you recommend based on my spending patterns?"
        response = llm.generate_response(query, data)
        logger.info("Generated response successfully")
        print("\nResponse:", response)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 