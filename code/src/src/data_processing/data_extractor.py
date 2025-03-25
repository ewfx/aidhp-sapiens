import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import logging

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

class DataExtractor:
    def __init__(self, data_dict):
        """Initialize the DataExtractor with loaded data."""
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
            self.transactions['Amount ($)'] = pd.to_numeric(self.transactions[amount_column])
            if 'Transaction Type' in self.transactions.columns:
                self.transactions.loc[self.transactions['Transaction Type'] == 'Debit', 'Amount ($)'] *= -1
            
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
            self.credit_card_transactions['Amount ($)'] = pd.to_numeric(self.credit_card_transactions[amount_column])
            if 'Transaction Type' in self.credit_card_transactions.columns:
                self.credit_card_transactions.loc[self.credit_card_transactions['Transaction Type'] == 'Debit', 'Amount ($)'] *= -1
            
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
        
        print(f"{GREEN}DataExtractor initialized successfully!{END}")
    
    def get_spending_summary(self) -> Dict[str, Any]:
        """Get a summary of user's spending patterns."""
        try:
            print(f"{BLUE}Generating spending summary...{END}")
            # Initialize spending data
            spending_data = {
                'total_spend': 0.0,
                'credit_card_spend': 0.0,
                'bank_spend': 0.0,
                'spending_by_category': {},
                'monthly_spending': {},
                'current_month_spending': 0.0,
                'last_month_spending': 0.0,
                'month_over_month_change': 0.0,
                'max_spending_category': '',
                'avg_transaction_amount': 0.0,
                'top_merchants': []
            }
            
            # Process bank transactions
            if not self.transactions.empty:
                bank_df = self.transactions.copy()
                bank_df['Date'] = pd.to_datetime(bank_df['Date'])
                bank_df['Amount'] = bank_df['Amount (USD)'].astype(float)
                # Make debits negative
                bank_df.loc[bank_df['Transaction Type'] == 'Debit', 'Amount'] *= -1
                
                # Add source and category
                bank_df['source'] = 'bank'
                if 'Category' not in bank_df.columns:
                    bank_df['Category'] = 'Uncategorized'
                
                # Calculate bank spend
                spending_data['bank_spend'] = abs(bank_df[bank_df['Amount'] < 0]['Amount'].sum())
            
            # Process credit card transactions
            if not self.credit_card_transactions.empty:
                cc_df = self.credit_card_transactions.copy()
                cc_df['Date'] = pd.to_datetime(cc_df['Date'])
                cc_df['Amount'] = cc_df['Amount ($)'].astype(float) * -1  # All credit card transactions are spending
                cc_df['source'] = 'credit_card'
                
                # Calculate credit card spend
                spending_data['credit_card_spend'] = abs(cc_df['Amount'].sum())
            
            # Combine transactions
            all_transactions = []
            if not self.transactions.empty:
                all_transactions.append(bank_df)
            if not self.credit_card_transactions.empty:
                all_transactions.append(cc_df)
            
            if all_transactions:
                combined_df = pd.concat(all_transactions, ignore_index=True)
                
                # Calculate total spend (negative amounts are spending)
                spending_data['total_spend'] = abs(combined_df[combined_df['Amount'] < 0]['Amount'].sum())
                
                # Calculate spending by category
                category_spending = combined_df[combined_df['Amount'] < 0].groupby('Category')['Amount'].sum()
                spending_data['spending_by_category'] = {cat: abs(amt) for cat, amt in category_spending.items()}
                
                # Calculate monthly spending
                monthly_spending = combined_df[combined_df['Amount'] < 0].groupby(
                    combined_df['Date'].dt.strftime('%Y-%m')
                )['Amount'].sum()
                spending_data['monthly_spending'] = {month: abs(amt) for month, amt in monthly_spending.items()}
                
                # Get current and last month spending
                current_month = pd.Timestamp.now().strftime('%Y-%m')
                last_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%Y-%m')
                
                spending_data['current_month_spending'] = abs(monthly_spending.get(current_month, 0))
                spending_data['last_month_spending'] = abs(monthly_spending.get(last_month, 0))
                
                # Calculate month over month change
                if spending_data['last_month_spending'] > 0:
                    spending_data['month_over_month_change'] = (
                        (spending_data['current_month_spending'] - spending_data['last_month_spending']) /
                        spending_data['last_month_spending'] * 100
                    )
                
                # Get maximum spending category
                if spending_data['spending_by_category']:
                    spending_data['max_spending_category'] = max(
                        spending_data['spending_by_category'].items(),
                        key=lambda x: x[1]
                    )[0]
                
                # Calculate average transaction amount
                spending_transactions = combined_df[combined_df['Amount'] < 0]
                if not spending_transactions.empty:
                    spending_data['avg_transaction_amount'] = abs(
                        spending_transactions['Amount'].mean()
                    )
                
                # Get top merchants by spend
                merchant_col = 'Merchant' if 'Merchant' in combined_df.columns else 'Receiver'
                merchant_spending = combined_df[combined_df['Amount'] < 0].groupby(merchant_col)['Amount'].sum()
                spending_data['top_merchants'] = [
                    {'merchant': merchant, 'amount': abs(amount)}
                    for merchant, amount in merchant_spending.nlargest(5).items()
                ]
            
            print(f"{GREEN}Spending summary generated successfully!{END}")
            return spending_data
        except Exception as e:
            print(f"{RED}Error generating spending summary: {str(e)}{END}")
            return {
                'total_spend': 0.0,
                'credit_card_spend': 0.0,
                'bank_spend': 0.0,
                'spending_by_category': {},
                'monthly_spending': {},
                'current_month_spending': 0.0,
                'last_month_spending': 0.0,
                'month_over_month_change': 0.0,
                'max_spending_category': '',
                'avg_transaction_amount': 0.0,
                'top_merchants': []
            }
    
    def get_kyc_details(self) -> Dict[str, Any]:
        """Extract KYC details and add demographic insights."""
        try:
            print(f"{BLUE}Extracting KYC details...{END}")
            if self.kyc.empty:
                print(f"{YELLOW}No KYC details available{END}")
                return {}
            
            kyc_data = self.kyc.iloc[0].to_dict()
            
            # Add demographic insights based on age and location
            age = kyc_data.get('Age', 0)
            location = kyc_data.get('Location', '')
            
            demographic_insights = {
                'age_group': self._get_age_group(age),
                'location_insights': self._get_location_insights(location),
                'typical_spending_patterns': self._get_typical_spending_patterns(age, location)
            }
            
            print(f"{GREEN}KYC details extracted successfully!{END}")
            return {**kyc_data, **demographic_insights}
        except Exception as e:
            print(f"{RED}Error extracting KYC details: {str(e)}{END}")
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
        top_merchants = self.get_spending_summary()['top_merchants'][:5]
        
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
                'travel': ['travel', 'vacation', 'trip', 'holiday', 'explore', 'adventure'],
                'technology': ['tech', 'gadget', 'computer', 'phone', 'coding', 'programming'],
                'food': ['restaurant', 'dining', 'food', 'cuisine', 'cooking', 'recipe'],
                'shopping': ['shopping', 'store', 'mall', 'buy', 'purchase', 'deal'],
                'entertainment': ['movie', 'music', 'concert', 'show', 'theater', 'performance'],
                'fitness': ['gym', 'workout', 'fitness', 'exercise', 'sports', 'training'],
                'education': ['study', 'course', 'learn', 'education', 'university', 'college'],
                'art': ['art', 'design', 'creative', 'painting', 'drawing', 'photography'],
                'gaming': ['game', 'gaming', 'console', 'playstation', 'xbox', 'nintendo'],
                'outdoor': ['hiking', 'camping', 'nature', 'park', 'outdoor', 'adventure']
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
        """Get available Wells Fargo products."""
        try:
            print(f"{BLUE}Getting available products...{END}")
            
            # Convert credit cards DataFrame to list of records
            credit_cards = self.credit_cards.to_dict('records') if not self.credit_cards.empty else []
            
            # Convert loans DataFrame to list of records
            loans = self.loans.to_dict('records') if not self.loans.empty else []
            
            products = {
                "credit_cards": credit_cards,
                "loans": loans
            }
            
            print(f"{GREEN}Available products retrieved successfully!{END}")
            return products
        except Exception as e:
            print(f"{RED}Error getting available products: {str(e)}{END}")
            return {"credit_cards": [], "loans": []}

    def get_user_interests(self):
        """Extract user interests based on spending patterns and social media."""
        interests = set()
        
        try:
            print(f"{BLUE}Analyzing user interests...{END}")
            
            # Get interests from spending categories
            spending_summary = self.get_spending_summary()
            if spending_summary:
                spend_by_category = spending_summary.get('spend_by_category', {})
                # Add categories where user spends significant amount
                for category, amount in spend_by_category.items():
                    if amount > 100:  # Threshold for significant spending
                        interests.add(category)
            
            # Extract interests from social media posts
            if not self.social_media.empty and 'Post Content' in self.social_media.columns:
                # Keywords that indicate interests
                interest_keywords = {
                    'travel': ['travel', 'vacation', 'trip', 'holiday'],
                    'technology': ['tech', 'gadget', 'computer', 'phone'],
                    'food': ['restaurant', 'dining', 'food', 'cuisine'],
                    'shopping': ['shopping', 'store', 'mall', 'buy'],
                    'entertainment': ['movie', 'music', 'concert', 'show'],
                    'fitness': ['gym', 'workout', 'fitness', 'exercise'],
                    'education': ['study', 'course', 'learn', 'education']
                }
                
                for post in self.social_media['Post Content'].astype(str):
                    post_lower = post.lower()
                    for category, keywords in interest_keywords.items():
                        if any(keyword in post_lower for keyword in keywords):
                            interests.add(category)
            
            print(f"{GREEN}User interests analyzed successfully!{END}")
            return list(interests)
        except Exception as e:
            print(f"{RED}Error extracting user interests: {str(e)}{END}")
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