from src.data_processing.data_loader import FinancialDataLoader
from src.data_processing.data_extractor import DataExtractor
from src.recommendation.product_recommender import ProductRecommender
import json
import logging
from src.utils.logger import setup_logger

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

# Set up logging
logger = setup_logger(__name__)

def save_json(data, filename):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Saved {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def main():
    try:
        # Initialize data loader
        data_loader = FinancialDataLoader()
        
        # Load all data
        data = data_loader.load_all_data()
        
        # Debug logging
        print("KYC Details:", data.get('kyc_details', {}))
        
        # Initialize data extractor
        data_extractor = DataExtractor(data)
        
        # Generate spending summary
        spending_summary = data_extractor.get_spending_summary()
        save_json(spending_summary, 'spending_analysis.json')
        
        # Extract KYC details
        kyc_details = data_extractor.get_kyc_details()
        save_json(kyc_details, 'kyc_details.json')
        
        # Extract user interests
        user_interests = data_extractor.get_user_interests()
        save_json(user_interests, 'user_interests.json')
        
        # Initialize product recommender
        product_recommender = ProductRecommender(
            spending_summary=spending_summary,
            kyc_details=kyc_details,
            user_interests=user_interests,
            available_products=data.get('credit_cards', []),
            available_loans=data.get('loans', [])
        )
        
        # Get product recommendations
        product_recommendations = product_recommender.get_product_recommendations()
        save_json(product_recommendations, 'product_recommendations.json')
        
        # Get credit card recommendations
        credit_card_recommendations = product_recommender.get_credit_card_recommendations()
        save_json(credit_card_recommendations, 'credit_card_recommendations.json')
        
        print("\n=== Final Recommendations ===\n")
        print("Product Recommendations:")
        print(json.dumps(product_recommendations, indent=2))
        print("\nCredit Card Recommendations:")
        print(json.dumps(credit_card_recommendations, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"{RED}Error: {str(e)}{END}")

if __name__ == "__main__":
    main() 