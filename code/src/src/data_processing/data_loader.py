import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Any

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

from src.config import DATA_FILES

class FinancialDataLoader:
    def __init__(self):
        self.transactions = None
        self.credit_card_transactions = None
        self.social_media = None
        self.kyc = None
        self.emails = None
        self.receiver_categories = None
        self.credit_cards = None
        self.loans = None
        self.credit_card_list = None

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all required data files."""
        try:
            print(f"{BLUE}Loading transaction data...{END}")
            self.transactions = self._load_transaction_data(DATA_FILES["transactions"])
            
            print(f"{BLUE}Loading credit card transactions...{END}")
            self.credit_card_transactions = self._load_transaction_data(DATA_FILES["credit_card_transactions"])
            
            print(f"{BLUE}Loading KYC details...{END}")
            self.kyc = self._load_kyc_details()
            
            print(f"{BLUE}Loading receiver categories...{END}")
            self.receiver_categories = self._load_receiver_categories()
            
            print(f"{BLUE}Loading social media data...{END}")
            self.social_media = self._load_social_media_data()
            
            print(f"{BLUE}Loading credit cards...{END}")
            self.credit_cards = self._load_credit_cards()
            
            print(f"{BLUE}Loading loans...{END}")
            self.loans = self._load_loans()
            
            print(f"{BLUE}Loading credit card list...{END}")
            self.credit_card_list = self._load_credit_card_list()
            
            print(f"{BLUE}Loading emails...{END}")
            self.emails = self._load_emails()
            
            print(f"{GREEN}All data loaded successfully!{END}")
            
            return {
                "transactions": self.transactions,
                "credit_card_transactions": self.credit_card_transactions,
                "social_media": self.social_media,
                "kyc": self.kyc,
                "emails": self.emails,
                "receiver_categories": self.receiver_categories,
                "credit_cards": self.credit_cards,
                "loans": self.loans,
                "credit_card_list": self.credit_card_list
            }
        except Exception as e:
            print(f"{RED}Error loading data: {str(e)}{END}")
            raise

    def _load_transaction_data(self, file_path: Path) -> pd.DataFrame:
        """Load transaction data from CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            # Convert Amount to numeric, ensuring debits are negative
            amount_column = 'Amount (USD)' if 'Amount (USD)' in df.columns else 'Amount ($)'
            if amount_column in df.columns:
                df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
                if 'Transaction Type' in df.columns:
                    df.loc[df['Transaction Type'].str.lower().str.contains('debit', na=False), amount_column] *= -1
            
            # Convert Date to datetime if it exists
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            
            return df
        except Exception as e:
            print(f"{RED}Error loading transaction data from {file_path}: {str(e)}{END}")
            return pd.DataFrame()

    def _load_kyc_details(self) -> pd.DataFrame:
        """Load KYC details from CSV file."""
        try:
            return pd.read_csv(DATA_FILES["kyc"])
        except Exception as e:
            print(f"{RED}Error loading KYC details: {str(e)}{END}")
            return pd.DataFrame()

    def _load_receiver_categories(self) -> pd.DataFrame:
        """Load receiver categories from CSV file."""
        try:
            return pd.read_csv(DATA_FILES["receiver_categories"])
        except Exception as e:
            print(f"{RED}Error loading receiver categories: {str(e)}{END}")
            return pd.DataFrame()

    def _load_social_media_data(self, custom_file: str = None) -> pd.DataFrame:
        """Load social media data from CSV file."""
        try:
            if custom_file:
                return pd.read_csv(custom_file)
            return pd.read_csv(DATA_FILES["social_media"])
        except Exception as e:
            print(f"{RED}Error loading social media data: {str(e)}{END}")
            return pd.DataFrame()

    def _load_credit_cards(self) -> pd.DataFrame:
        """Load credit card details from CSV file."""
        try:
            df = pd.read_csv(DATA_FILES["credit_cards"])
            # Convert numeric columns
            numeric_columns = ['Annual Fee (USD)', 'Interest Rate (%)']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            print(f"{RED}Error loading credit card details: {str(e)}{END}")
            return pd.DataFrame()

    def _load_loans(self) -> pd.DataFrame:
        """Load loan details from CSV file."""
        try:
            df = pd.read_csv(DATA_FILES["loans"])
            # Convert numeric columns
            numeric_columns = ['Interest Rate (%)', 'Loan Amount (USD)', 'Monthly EMI (USD)']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            print(f"{RED}Error loading loan details: {str(e)}{END}")
            return pd.DataFrame()

    def _load_credit_card_list(self) -> pd.DataFrame:
        """Load credit card list from CSV file."""
        try:
            df = pd.read_csv(DATA_FILES["credit_card_list"])
            # Convert numeric columns
            if 'Credit Limit (USD)' in df.columns:
                df['Credit Limit (USD)'] = pd.to_numeric(df['Credit Limit (USD)'], errors='coerce')
            if 'Current Balance (USD)' in df.columns:
                df['Current Balance (USD)'] = pd.to_numeric(df['Current Balance (USD)'], errors='coerce')
            return df
        except Exception as e:
            print(f"{RED}Error loading credit card list: {str(e)}{END}")
            return pd.DataFrame()

    def _load_emails(self) -> pd.DataFrame:
        """Load email data from CSV file."""
        try:
            return pd.read_csv(DATA_FILES["emails"])
        except Exception as e:
            print(f"{RED}Error loading email data: {str(e)}{END}")
            return pd.DataFrame()

    def preprocess_transactions(self) -> pd.DataFrame:
        """Preprocess transaction data for analysis."""
        if self.transactions is None:
            raise ValueError("Transaction data not loaded")

        df = self.transactions.copy()
        
        # Handle missing values
        df = df.fillna({
            'Amount ($)': 0,
            'Category': 'uncategorized',
            'Receiver': 'unknown'
        })

        return df

    def get_spending_categories(self) -> Dict[str, float]:
        """Calculate total spending by category."""
        if self.transactions is None:
            raise ValueError("Transaction data not loaded")

        df = self.preprocess_transactions()
        return df.groupby('Category')['Amount ($)'].sum().to_dict()

    def get_monthly_summary(self) -> pd.DataFrame:
        """Generate monthly summary of transactions."""
        if self.transactions is None:
            raise ValueError("Transaction data not loaded")

        df = self.preprocess_transactions()
        df['month'] = df['Date'].dt.to_period('M')
        return df.groupby('month').agg({
            'Amount ($)': ['sum', 'mean', 'count'],
            'Category': lambda x: x.value_counts().index[0]  # Most common category
        }).round(2)

    def get_credit_card_usage(self) -> pd.DataFrame:
        """Analyze credit card usage patterns."""
        if self.credit_card_transactions is None or self.credit_card_list is None:
            raise ValueError("Credit card data not loaded")

        transactions = self.credit_card_transactions.copy()
        cards = self.credit_card_list.copy()

        # Merge transaction data with card information
        merged_data = pd.merge(transactions, cards, on='Card ID', how='left')
        
        # Convert dates
        merged_data['Date'] = pd.to_datetime(merged_data['Date'])
        merged_data['Issued Date'] = pd.to_datetime(merged_data['Issued Date'])
        merged_data['Expiry Date'] = pd.to_datetime(merged_data['Expiry Date'])

        return merged_data 