import argparse
import json
import pandas as pd
from pathlib import Path
from src.data_processing.data_loader import FinancialDataLoader
from src.data_processing.data_extractor import DataExtractor
from src.ai.llm_interaction import LLMInteraction

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

def save_json(data: dict, filename: str):
    """Save data to a JSON file."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / filename
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"{GREEN}✓ Saved {filename}{END}")

def update_recommendations(new_posts_file: str):
    """Update recommendations based on new social media posts."""
    try:
        # Load existing data
        with open("output/spending_analysis.json", 'r') as f:
            spending_data = json.load(f)
        with open("output/kyc_details.json", 'r') as f:
            kyc_details = json.load(f)
        with open("output/user_interests.json", 'r') as f:
            user_interests = json.load(f)
        with open("output/product_recommendations.json", 'r') as f:
            product_recommendations = json.load(f)
        with open("output/credit_card_recommendations.json", 'r') as f:
            credit_card_recommendations = json.load(f)

        # Load new posts
        data_loader = FinancialDataLoader()
        new_posts = data_loader._load_social_media_data(new_posts_file)

        # Extract new information
        data_extractor = DataExtractor({
            'social_media': new_posts,
            'kyc': pd.DataFrame([kyc_details])
        })
        
        # Update user interests and KYC details
        new_interests = data_extractor.get_user_interests()
        updated_interests = list(set(user_interests + new_interests))  # Remove duplicates
        
        # Update KYC details with new interests
        kyc_details['Interests'] = ', '.join(updated_interests)
        kyc_details['Hobbies'] = ', '.join(updated_interests)  # Using same interests for hobbies

        # Generate new recommendations
        llm = LLMInteraction()
        new_product_recommendations = llm.get_product_recommendations(
            spending_data=spending_data,
            kyc_details=kyc_details,
            user_interests=updated_interests,
            available_products=product_recommendations.get('available_products', {})
        )

        new_credit_card_recommendations = llm.get_credit_card_recommendations(
            spending_data=spending_data,
            kyc_details=kyc_details,
            user_interests=updated_interests,
            available_products=product_recommendations.get('available_products', {})
        )

        # Save updated data
        save_json(updated_interests, "user_interests.json")
        save_json(kyc_details, "kyc_details.json")
        save_json(new_product_recommendations, "product_recommendations.json")
        save_json(new_credit_card_recommendations, "credit_card_recommendations.json")

        print(f"\n{GREEN}=== Updated Recommendations ==={END}")
        print("\nUpdated Product Recommendations:")
        print(json.dumps(new_product_recommendations, indent=2))
        
        print("\nUpdated Credit Card Recommendations:")
        print(json.dumps(new_credit_card_recommendations, indent=2))

    except Exception as e:
        print(f"{RED}Error updating recommendations: {str(e)}{END}")
        raise

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Personalized Banking Services')
    parser.add_argument('--update-social', type=str, help='Update recommendations with new social media posts file')
    args = parser.parse_args()

    if args.update_social:
        update_recommendations(args.update_social)
        return

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    data_loader = FinancialDataLoader()
    data = data_loader.load_all_data()
    
    # Extract information
    data_extractor = DataExtractor(data)
    spending_data = data_extractor.get_spending_summary()
    kyc_details = data_extractor.get_kyc_details()
    user_interests = data_extractor.get_user_interests()
    available_products = data_extractor.get_available_products()
    
    # Generate recommendations
    llm = LLMInteraction()
    product_recommendations = llm.get_product_recommendations(
        spending_data=spending_data,
        kyc_details=kyc_details,
        user_interests=user_interests,
        available_products=available_products
    )
    
    credit_card_recommendations = llm.get_credit_card_recommendations(
        spending_data=spending_data,
        kyc_details=kyc_details,
        user_interests=user_interests,
        available_products=available_products
    )
    
    # Save results
    save_json(spending_data, "spending_analysis.json")
    save_json(kyc_details, "kyc_details.json")
    save_json(user_interests, "user_interests.json")
    save_json(product_recommendations, "product_recommendations.json")
    save_json(credit_card_recommendations, "credit_card_recommendations.json")
    
    # Print final output
    print(f"\n{GREEN}=== Final Recommendations ==={END}")
    print("\nProduct Recommendations:")
    print(json.dumps(product_recommendations, indent=2))
    
    print("\nCredit Card Recommendations:")
    print(json.dumps(credit_card_recommendations, indent=2))

if __name__ == "__main__":
    main()
