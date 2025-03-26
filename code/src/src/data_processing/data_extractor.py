import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
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

class DataExtractor:
    def __init__(self, data_dict):
        """Initialize the DataExtractor with loaded data."""
        logger.info("Initializing DataExtractor")
        print(f"{BLUE}Initializing DataExtractor...{END}")
        self.transactions = data_dict.get('transactions', pd.DataFrame())
        self.credit_card_transactions = data_dict.get('credit_card_transactions', pd.DataFrame())
        self.social_media = data_dict.get('social_media', pd.DataFrame())
        self.kyc = data_dict.get('kyc', pd.DataFrame())
        self.receiver_categories = data_dict.get('receiver_categories', pd.DataFrame())
        self.credit_cards = data_dict.get('credit_cards', pd.DataFrame())
        self.loans = data_dict.get('loans', pd.DataFrame())
        self.credit_card_list = data_dict.get('credit_card_list', pd.DataFrame())
        self.emails = data_dict.get('emails', pd.DataFrame())
        
        # Process transactions
        if not self.transactions.empty:
            # Convert amount to numeric, ensuring debits are negative
            amount_column = 'Amount (USD)' if 'Amount (USD)' in self.transactions.columns else 'Amount ($)'
            self.transactions[amount_column] = pd.to_numeric(self.transactions[amount_column], errors='coerce')
            if 'Transaction Type' in self.transactions.columns:
                self.transactions.loc[self.transactions['Transaction Type'].str.lower().str.contains('debit', na=False), amount_column] *= -1
            
            # Merge with categories if Category column doesn't exist
            if 'Category' not in self.transactions.columns and not self.receiver_categories.empty:
                self.transactions = self.transactions.merge(
                    self.receiver_categories,
                    on='Receiver',
                    how='left'
                )
                self.transactions['Category'] = self.transactions['Category'].fillna('Other')
        
        # Process credit card transactions
        if not self.credit_card_transactions.empty:
            # Convert amount to numeric, ensuring debits are negative
            amount_column = 'Amount (USD)' if 'Amount (USD)' in self.credit_card_transactions.columns else 'Amount ($)'
            self.credit_card_transactions[amount_column] = pd.to_numeric(self.credit_card_transactions[amount_column], errors='coerce')
            if 'Transaction Type' in self.credit_card_transactions.columns:
                self.credit_card_transactions.loc[self.credit_card_transactions['Transaction Type'].str.lower().str.contains('debit', na=False), amount_column] *= -1
            
            # Fill any missing categories with 'Other'
            if 'Category' in self.credit_card_transactions.columns:
                self.credit_card_transactions['Category'] = self.credit_card_transactions['Category'].fillna('Other')
            # Merge with categories if Category column doesn't exist
            elif not self.receiver_categories.empty:
                # Rename Merchant to Receiver for merging
                self.credit_card_transactions = self.credit_card_transactions.rename(columns={'Merchant': 'Receiver'})
                self.credit_card_transactions = self.credit_card_transactions.merge(
                    self.receiver_categories,
                    on='Receiver',
                    how='left'
                )
                self.credit_card_transactions['Category'] = self.credit_card_transactions['Category'].fillna('Other')
                # Rename back to Merchant
                self.credit_card_transactions = self.credit_card_transactions.rename(columns={'Receiver': 'Merchant'})
        
        logger.debug("DataExtractor initialized successfully")
    
    def get_spending_summary(self) -> Dict[str, Any]:
        """Get a summary of user's spending patterns."""
        logger.info("Generating spending summary")
        try:
            print(f"{BLUE}Generating spending summary...{END}")
            spending_data = self._generate_spending_summary()
            print(f"{GREEN}Spending summary generated successfully!{END}")
            logger.info("Successfully generated spending summary")
            return spending_data
        except Exception as e:
            print(f"{RED}Error generating spending summary: {str(e)}{END}")
            logger.error(f"Error generating spending summary: {str(e)}")
            return {
                'total_spend': 0.0,
                'credit_card_spend': 0.0,
                'bank_spend': 0.0,
                'spending_by_category': {},
                'monthly_spending': {},
                'current_month_spend': 0.0,
                'last_month_spend': 0.0,
                'month_over_month_change': 0.0,
                'max_spending_category': None,
                'average_transaction_amount': 0.0,
                'top_merchants_by_spend': {}
            }
    
    def _generate_spending_summary(self):
        spending_data = {}
        
        # Process bank transactions
        bank_spend = 0.0
        if self.transactions.empty:
            logger.warning("No bank transactions available")
        else:
            # Convert Amount to float if it's not already
            self.transactions['Amount (USD)'] = self.transactions['Amount (USD)'].astype(float)
            
            # Calculate bank spend (debits are spending)
            debit_mask = self.transactions['Transaction Type'] == 'Debit'
            bank_spend = self.transactions.loc[debit_mask, 'Amount (USD)'].sum()
            logger.info(f"Bank spend: {bank_spend}")
        
        # Process credit card transactions
        credit_card_spend = 0.0
        if self.credit_card_transactions.empty:
            logger.warning("No credit card transactions available")
        else:
            # Convert Amount to float if it's not already
            self.credit_card_transactions['Amount ($)'] = self.credit_card_transactions['Amount ($)'].astype(float)
            
            # All credit card transactions are spending
            credit_card_spend = self.credit_card_transactions['Amount ($)'].sum()
            logger.info(f"Credit card spend: {credit_card_spend}")
        
        # Calculate total spend
        total_spend = bank_spend + credit_card_spend
        logger.info(f"Total spend: {total_spend}")
        
        # Combine transactions for analysis
        all_transactions = []
        
        if not self.transactions.empty:
            bank_txns = self.transactions.copy()
            bank_txns['source'] = 'bank'
            bank_txns['category'] = bank_txns['Receiver'].apply(self._categorize_transaction)
            bank_txns['amount'] = bank_txns.apply(
                lambda x: x['Amount (USD)'] if x['Transaction Type'] == 'Debit' else 0, 
                axis=1
            )
            all_transactions.append(bank_txns[['Date', 'amount', 'category', 'source', 'Receiver']])
        
        if not self.credit_card_transactions.empty:
            cc_txns = self.credit_card_transactions.copy()
            cc_txns['source'] = 'credit_card'
            cc_txns['category'] = cc_txns['Merchant'].apply(self._categorize_transaction)
            cc_txns['amount'] = cc_txns['Amount ($)']
            all_transactions.append(cc_txns[['Date', 'amount', 'category', 'source', 'Merchant']])
        
        if all_transactions:
            combined_txns = pd.concat(all_transactions, ignore_index=True)
            combined_txns['Date'] = pd.to_datetime(combined_txns['Date'])
            
            # Calculate spending by category
            spending_by_category = combined_txns.groupby('category')['amount'].sum().to_dict()
            
            # Calculate monthly spending
            monthly_spending = combined_txns.groupby(combined_txns['Date'].dt.strftime('%Y-%m'))['amount'].sum().to_dict()
            
            # Calculate current month and last month spending
            current_month = datetime.now().strftime('%Y-%m')
            last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
            
            current_month_spend = monthly_spending.get(current_month, 0)
            last_month_spend = monthly_spending.get(last_month, 0)
            
            # Calculate month over month change
            if last_month_spend != 0:
                mom_change = ((current_month_spend - last_month_spend) / last_month_spend) * 100
            else:
                mom_change = 0
            
            # Get maximum spending category
            max_spending_category = max(spending_by_category.items(), key=lambda x: x[1])[0] if spending_by_category else None
            
            # Calculate average transaction amount
            avg_transaction = combined_txns['amount'].mean()
            
            # Get top merchants by spend
            top_merchants = combined_txns.groupby('Merchant' if 'Merchant' in combined_txns.columns else 'Receiver')['amount'].sum().nlargest(5).to_dict()
            
            spending_data = {
                'total_spend': total_spend,
                'bank_spend': bank_spend,
                'credit_card_spend': credit_card_spend,
                'spending_by_category': spending_by_category,
                'monthly_spending': monthly_spending,
                'current_month_spend': current_month_spend,
                'last_month_spend': last_month_spend,
                'month_over_month_change': mom_change,
                'max_spending_category': max_spending_category,
                'average_transaction_amount': avg_transaction,
                'top_merchants_by_spend': top_merchants
            }
        else:
            logger.warning("No transactions available for analysis")
            spending_data = {
                'total_spend': 0,
                'bank_spend': 0,
                'credit_card_spend': 0,
                'spending_by_category': {},
                'monthly_spending': {},
                'current_month_spend': 0,
                'last_month_spend': 0,
                'month_over_month_change': 0,
                'max_spending_category': None,
                'average_transaction_amount': 0,
                'top_merchants_by_spend': {}
            }
        
        return spending_data
    
    def get_kyc_details(self) -> Dict[str, Any]:
        """Extract KYC details and add demographic insights."""
        logger.info("Extracting KYC details")
        try:
            print(f"{BLUE}Extracting KYC details...{END}")
            if isinstance(self.kyc, pd.DataFrame) and self.kyc.empty:
                print(f"{YELLOW}No KYC details available{END}")
                return {}
            
            # Handle both DataFrame and dict formats
            if isinstance(self.kyc, pd.DataFrame):
                kyc_data = self.kyc.iloc[0].to_dict()
            else:
                kyc_data = self.kyc
            
            # Add demographic insights based on age and location
            age = kyc_data.get('Age', 0)
            location = kyc_data.get('Location', '')
            
            demographic_insights = {
                'age_group': self._get_age_group(age),
                'location_insights': self._get_location_insights(location),
                'typical_spending_patterns': self._get_typical_spending_patterns(age, location)
            }
            
            print(f"{GREEN}KYC details extracted successfully!{END}")
            logger.debug("Successfully extracted KYC details")
            return {**kyc_data, **demographic_insights}
        except Exception as e:
            print(f"{RED}Error extracting KYC details: {str(e)}{END}")
            logger.error(f"Error extracting KYC details: {str(e)}")
            return {}
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group for demographic analysis."""
        if age < 25:
            return "young_professional"
        elif age < 35:
            return "early_career"
        elif age < 45:
            return "mid_career"
        elif age < 55:
            return "established_professional"
        else:
            return "senior"
    
    def _get_location_insights(self, location: str) -> Dict[str, Any]:
        """Get insights based on location."""
        # This would typically come from a demographic database
        # For now, returning placeholder data
        return {
            'cost_of_living': 'high' if 'New York' in location or 'San Francisco' in location else 'medium',
            'typical_activities': ['Dining', 'Entertainment', 'Shopping'],
            'market_segment': 'urban' if 'New York' in location or 'San Francisco' in location else 'suburban'
        }
    
    def _get_typical_spending_patterns(self, age: int, location: str) -> Dict[str, Any]:
        """Get typical spending patterns based on age and location."""
        age_group = self._get_age_group(age)
        location_insights = self._get_location_insights(location)
        
        # This would typically come from demographic research
        # For now, returning placeholder data
        return {
            'common_categories': ['Dining', 'Entertainment', 'Shopping'],
            'typical_merchants': ['Restaurants', 'Retail Stores', 'Entertainment Venues'],
            'spending_trends': ['Online Shopping', 'Experiences', 'Health & Wellness']
        }
    
    def get_social_media_posts(self) -> List[Dict[str, Any]]:
        """Extract social media posts."""
        if self.social_media.empty:
            return []
            
        return self.social_media.to_dict('records')
    
    def analyze_user_interests(self) -> Dict[str, Any]:
        """Analyze user interests and preferences based on transaction data and social media."""
        # Get top spending categories
        spending_by_category = self.get_spending_summary()['spending_by_category']
        top_categories = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get top merchants
        top_merchants = self.get_spending_summary()['top_merchants_by_spend'][:5]
        
        # Map categories to interests
        category_to_interest = {
            'Dining': ['Food', 'Restaurants', 'Culinary'],
            'Entertainment': ['Entertainment', 'Movies', 'Streaming'],
            'Fitness': ['Fitness', 'Health', 'Sports'],
            'Shopping': ['Shopping', 'Retail'],
            'Transport': ['Travel', 'Transportation'],
            'Grocery': ['Cooking', 'Food'],
            'Subscription': ['Entertainment', 'Streaming', 'Digital Services'],
            'Investment': ['Finance', 'Investing'],
            'Fashion': ['Fashion', 'Clothing', 'Style'],
            'Electronics': ['Technology', 'Gadgets']
        }
        
        # Infer interests from categories
        interests = set()
        for category, amount in top_categories:
            if category in category_to_interest:
                interests.update(category_to_interest[category])
        
        # Infer preferences from merchants
        preferences = {
            'shopping': [],
            'entertainment': [],
            'dining': [],
            'fitness': [],
            'travel': []
        }
        
        for merchant in top_merchants:
            merchant_name = merchant['merchant'].lower()
            if any(store in merchant_name for store in ['amazon', 'walmart', 'target']):
                preferences['shopping'].append('Online Shopping')
            elif any(store in merchant_name for store in ['netflix', 'spotify', 'hulu']):
                preferences['entertainment'].append('Streaming')
            elif any(store in merchant_name for store in ['starbucks', 'restaurant', 'cafe']):
                preferences['dining'].append('Dining Out')
            elif any(store in merchant_name for store in ['gym', 'fitness', 'equinox']):
                preferences['fitness'].append('Gym')
            elif any(store in merchant_name for store in ['airline', 'hotel', 'booking']):
                preferences['travel'].append('Travel')
        
        # Clean up empty preferences
        preferences = {k: v for k, v in preferences.items() if v}
        
        # Analyze social media posts for additional interests
        social_media_interests = set()
        if not self.social_media.empty and 'Post Content' in self.social_media.columns:
            # Keywords that indicate interests
            interest_keywords = {
                'travel': ['travel', 'vacation', 'trip', 'holiday', 'explore', 'adventure', 'beach', 'ocean', 'waves'],
                'technology': ['tech', 'gadget', 'computer', 'phone', 'coding', 'programming', 'ai', 'innovation'],
                'food': ['restaurant', 'dining', 'food', 'cuisine', 'cooking', 'recipe', 'pasta', 'dinner'],
                'shopping': ['shopping', 'store', 'mall', 'buy', 'purchase', 'deal', 'wardrobe', 'fashion'],
                'entertainment': ['movie', 'music', 'concert', 'show', 'theater', 'performance', 'documentary'],
                'fitness': ['gym', 'workout', 'fitness', 'exercise', 'sports', 'training', 'swimming', 'deadlifts'],
                'education': ['study', 'course', 'learn', 'education', 'university', 'college', 'career'],
                'finance': ['investing', 'finance', 'stock', 'market', 'savings', 'investments', 'financial'],
                'outdoor': ['hiking', 'camping', 'nature', 'park', 'outdoor', 'adventure', 'beach', 'ocean'],
                'lifestyle': ['weekend', 'relax', 'vibes', 'life', 'journey', 'experience']
            }
            
            for post in self.social_media['Post Content'].astype(str):
                post_lower = post.lower()
                for category, keywords in interest_keywords.items():
                    if any(keyword in post_lower for keyword in keywords):
                        social_media_interests.add(category)
        
        # Combine interests from both sources
        combined_interests = interests.union(social_media_interests)
        
        return {
            "spending_habits": list(interests),  # Keep spending habits separate
            "hobbies": list(combined_interests),  # Combined interests from both sources
            "frequent_activities": [merchant['merchant'] for merchant in top_merchants],
            "preferences": preferences,
            "social_media_interests": list(social_media_interests)  # Add social media interests separately
        }
    
    def get_available_products(self) -> Dict[str, Any]:
        """Get available financial products."""
        logger.info("Getting available products")
        try:
            print(f"{BLUE}Getting available products...{END}")
            
            products = {
                'credit_cards': [],
                'loans': []
            }
            
            # Process credit cards
            if isinstance(self.credit_cards, pd.DataFrame) and not self.credit_cards.empty:
                products['credit_cards'] = self.credit_cards.to_dict('records')
            
            # Process loans
            if isinstance(self.loans, pd.DataFrame) and not self.loans.empty:
                products['loans'] = self.loans.to_dict('records')
            
            logger.info(f"Found {len(products['credit_cards'])} credit cards and {len(products['loans'])} loans")
            return products
            
        except Exception as e:
            logger.error(f"Error getting available products: {str(e)}")
            return {'credit_cards': [], 'loans': []}

    def get_user_interests(self) -> List[str]:
        """Extract user interests from social media data."""
        logger.info("Extracting user interests")
        try:
            print(f"{BLUE}Analyzing user interests...{END}")
            
            if not isinstance(self.social_media, pd.DataFrame) or self.social_media.empty:
                logger.warning("No social media data available")
                return []
            
            # Keywords that indicate interests
            interest_keywords = {
                'travel': ['travel', 'vacation', 'trip', 'holiday', 'explore', 'adventure', 'beach', 'ocean', 'waves'],
                'technology': ['tech', 'gadget', 'computer', 'phone', 'coding', 'programming', 'ai', 'innovation'],
                'food': ['restaurant', 'dining', 'food', 'cuisine', 'cooking', 'recipe', 'pasta', 'dinner'],
                'shopping': ['shopping', 'store', 'mall', 'buy', 'purchase', 'deal', 'wardrobe', 'fashion'],
                'entertainment': ['movie', 'music', 'concert', 'show', 'theater', 'performance', 'documentary'],
                'fitness': ['gym', 'workout', 'fitness', 'exercise', 'sports', 'training', 'swimming', 'deadlifts'],
                'education': ['study', 'course', 'learn', 'education', 'university', 'college', 'career'],
                'finance': ['investing', 'finance', 'stock', 'market', 'savings', 'investments', 'financial'],
                'outdoor': ['hiking', 'camping', 'nature', 'park', 'outdoor', 'adventure', 'beach', 'ocean'],
                'lifestyle': ['weekend', 'relax', 'vibes', 'life', 'journey', 'experience']
            }
            
            # Extract interests from social media posts
            interests = set()
            
            # Process Post Content column
            if 'Post Content' in self.social_media.columns:
                for content in self.social_media['Post Content']:
                    if isinstance(content, str):
                        content_lower = content.lower()
                        for category, keywords in interest_keywords.items():
                            if any(keyword in content_lower for keyword in keywords):
                                interests.add(category)
            
            # Convert set to list and sort
            interests_list = sorted(list(interests))
            logger.info(f"Extracted {len(interests_list)} interests: {', '.join(interests_list)}")
            return interests_list
            
        except Exception as e:
            logger.error(f"Error extracting user interests: {str(e)}")
            return []
        
    def get_credit_profile(self):
        """Extract credit-related information."""
        try:
            print(f"{BLUE}Extracting credit profile...{END}")
            credit_profile = {
                'total_credit_limit': 0,
                'current_balance': 0,
                'utilization_rate': 0,
                'payment_history': 'Good',  # Default value
                'avg_monthly_spend': 0
            }
            
            if not self.credit_card_list.empty:
                # Calculate total credit limit and current balance
                credit_profile['total_credit_limit'] = self.credit_card_list['Credit Limit (USD)'].sum()
                credit_profile['current_balance'] = self.credit_card_list['Current Balance (USD)'].sum()
                
                # Calculate utilization rate
                if credit_profile['total_credit_limit'] > 0:
                    credit_profile['utilization_rate'] = (credit_profile['current_balance'] / credit_profile['total_credit_limit']) * 100
            
            # Calculate average monthly spend from credit card transactions
            if not self.credit_card_transactions.empty:
                monthly_spend = self.credit_card_transactions.groupby(
                    pd.to_datetime(self.credit_card_transactions['Date']).dt.to_period('M')
                )['Amount ($)'].sum().abs()
                credit_profile['avg_monthly_spend'] = monthly_spend.mean()
            
            print(f"{GREEN}Credit profile extracted successfully!{END}")
            return credit_profile
        except Exception as e:
            print(f"{RED}Error extracting credit profile: {str(e)}{END}")
            return {}

    def _categorize_transaction(self, merchant: str) -> str:
        """Categorize a transaction based on the merchant name."""
        merchant = merchant.lower()
        
        categories = {
            'dining': ['restaurant', 'starbucks'],
            'shopping': ['amazon', 'walmart', 'costco', 'best buy', 'nike', 'apple'],
            'entertainment': ['netflix', 'spotify'],
            'travel': ['airline', 'hotel', 'airbnb', 'uber'],
            'transportation': ['tesla', 'supercharger'],
            'fitness': ['gym'],
            'insurance': ['insurance'],
            'investments': ['equity', 'mutual funds'],
            'electronics': ['electronic', 'gadgets'],
            'uncategorized': []
        }
        
        for category, keywords in categories.items():
            if any(keyword in merchant for keyword in keywords):
                return category
        
        return 'uncategorized' 