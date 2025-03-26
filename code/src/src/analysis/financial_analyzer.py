import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from src.utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

class FinancialAnalyzer:
    def __init__(self, data: Dict[str, pd.DataFrame]):
        """Initialize the financial analyzer with loaded data."""
        logger.info("Initializing FinancialAnalyzer")
        self.transactions = data.get('transactions', pd.DataFrame())
        self.credit_card = data.get('credit_card', pd.DataFrame())
        self.kyc = data.get('kyc', pd.DataFrame())
        self.social_media = data.get('social_media', pd.DataFrame())
        self.emails = data.get('emails', pd.DataFrame())
        self.credit_cards = data.get('credit_cards', pd.DataFrame())
        self.receiver_categories = data.get('receiver_categories', pd.DataFrame())
        
        # Merge transactions with receiver categories
        if not self.transactions.empty and not self.receiver_categories.empty:
            self.transactions = self.transactions.merge(
                self.receiver_categories,
                on='Receiver',
                how='left'
            )
        logger.debug("Financial analyzer initialized with input data")
    
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns from transaction data."""
        logger.info("Analyzing spending patterns")
        try:
            if self.transactions.empty:
                logger.warning("No transaction data found")
                return {}
            
            # Calculate total spending by category
            category_spending = self.transactions.groupby('Category')['Amount ($)'].sum().sort_values(ascending=False)
            
            # Calculate monthly spending trends
            monthly_spending = self.transactions.groupby(self.transactions['Date'].dt.to_period('M'))['Amount ($)'].sum()
            
            # Calculate average transaction amount by category
            avg_transaction = self.transactions.groupby('Category')['Amount ($)'].mean()
            
            # Identify top merchants by spending
            top_merchants = self.transactions.groupby('Receiver')['Amount ($)'].sum().sort_values(ascending=False).head(10)
            
            analysis = {
                'category_spending': category_spending.to_dict(),
                'monthly_spending': monthly_spending.to_dict(),
                'avg_transaction': avg_transaction.to_dict(),
                'top_merchants': top_merchants.to_dict()
            }
            logger.info("Successfully analyzed spending patterns")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {str(e)}")
            return {}
    
    def identify_spending_clusters(self) -> Dict[str, Any]:
        """Identify spending clusters using K-means clustering."""
        if self.transactions.empty:
            return {}
            
        # Prepare data for clustering
        X = self.transactions[['Amount ($)']].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        self.transactions['Cluster'] = kmeans.fit_predict(X_scaled)
        
        # Analyze clusters
        cluster_analysis = self.transactions.groupby('Cluster').agg({
            'Amount ($)': ['count', 'mean', 'sum'],
            'Category': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown'
        }).round(2)
        
        return {
            'cluster_analysis': cluster_analysis.to_dict(),
            'cluster_labels': ['Low', 'Medium', 'High']
        }
    
    def analyze_credit_card_usage(self) -> Dict[str, Any]:
        """Analyze credit card usage patterns."""
        logger.info("Analyzing credit card usage")
        try:
            if self.credit_card.empty:
                logger.warning("No credit card transaction data found")
                return {}
            
            # Calculate total credit card spending
            total_spending = self.credit_card['Amount ($)'].sum()
            
            # Calculate spending by category
            category_spending = self.credit_card.groupby('Category')['Amount ($)'].sum()
            
            # Calculate average transaction amount
            avg_transaction = self.credit_card['Amount ($)'].mean()
            
            # Calculate credit utilization (placeholder since we don't have credit limit data)
            credit_utilization = 0.0  # This would be calculated if credit limit data was available
            
            analysis = {
                'total_spending': total_spending,
                'category_spending': category_spending.to_dict(),
                'avg_transaction': avg_transaction,
                'credit_utilization': credit_utilization
            }
            logger.info("Successfully analyzed credit card usage")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing credit card usage: {str(e)}")
            return {}
    
    def generate_savings_recommendations(self) -> Dict[str, Any]:
        """Generate personalized savings recommendations."""
        if self.transactions.empty:
            return {}
            
        # Analyze subscription spending
        subscription_categories = ['streaming', 'subscription', 'membership']
        subscription_spending = self.transactions[
            self.transactions['Category'].str.lower().isin(subscription_categories)
        ]['Amount ($)'].sum()
        
        # Identify high-value transactions (top 10%)
        high_value_threshold = self.transactions['Amount ($)'].quantile(0.9)
        high_value_transactions = self.transactions[
            self.transactions['Amount ($)'] > high_value_threshold
        ]
        
        # Calculate potential savings
        subscription_savings = subscription_spending * 0.20  # 20% optimization potential
        impulse_savings = high_value_transactions['Amount ($)'].sum() * 0.15  # 15% reduction potential
        
        return {
            'subscription_spending': subscription_spending,
            'subscription_savings': subscription_savings,
            'high_value_transactions': high_value_transactions['Amount ($)'].sum(),
            'impulse_savings': impulse_savings,
            'total_potential_savings': subscription_savings + impulse_savings
        }

    def calculate_credit_score_factors(self) -> Dict[str, float]:
        """Calculate factors that might influence credit score."""
        df = self.transactions.copy()
        
        # Calculate payment consistency
        df['month'] = df['Date'].dt.to_period('M')
        monthly_payments = df.groupby('month')['Amount ($)'].sum()
        payment_consistency = monthly_payments.std() / monthly_payments.mean()
        
        # Calculate spending diversity
        category_counts = df['Category'].nunique()
        total_categories = len(df['Category'].unique())
        spending_diversity = category_counts / total_categories
        
        return {
            'payment_consistency': payment_consistency,
            'spending_diversity': spending_diversity
        } 