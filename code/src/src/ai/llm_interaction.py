from typing import Dict, Any, List
from pathlib import Path
from llama_cpp import Llama
import json
import pandas as pd
from src.config import LLM_MODEL_PATH

class LLMInteraction:
    def __init__(self):
        """Initialize the LLM interaction with Mistral model."""
        print("\033[94mInitializing Mistral model...\033[0m")  # Blue color for initialization
        self.llm = Llama(
            model_path=str(LLM_MODEL_PATH),
            n_ctx=4096,  # Context window
            n_threads=10,  # Use all 10 CPU cores
            n_gpu_layers=10,  # Use all 10 GPU cores
            verbose=True
        )
        print("\033[92mMistral model initialized successfully!\033[0m")  # Green color for success
        
    def _generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using Mistral model."""
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            echo=False,
            stop=["</s>", "Human:", "Assistant:"]
        )
        content = response['choices'][0]['text'].strip()
        
        # Extract JSON from the response if it contains text before/after
        try:
            # Find the first '{' and last '}'
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return content[start:end]
            return content
        except Exception:
            return content
        
    def get_product_recommendations(self, spending_data: Dict[str, Any], kyc_details: Dict[str, Any], user_interests: List[str], available_products: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product recommendations based on user data."""
        try:
            # Convert credit cards data to the expected format
            credit_cards = []
            if 'credit_cards' in available_products:
                for card in available_products['credit_cards']:
                    credit_cards.append({
                        "name": card['Credit Card Name'],
                        "annual_fee": float(card['Annual Fee (USD)']),
                        "credit_limit": float(card['Credit Limit (USD)']),
                        "interest_rate": float(card['Interest Rate (%)']),
                        "benefits": card['Benefits'].split(','),
                        "rewards_rate": card['Rewards & Cashback'],
                        "other_perks": card['Other Perks'].split(',') if card['Other Perks'] else []
                    })

            # Get top merchants list
            top_merchants = []
            if 'top_merchants' in spending_data:
                top_merchants = [merchant['merchant'] for merchant in spending_data['top_merchants']]

            # Get spending categories
            spending_categories = []
            if 'spending_by_category' in spending_data:
                spending_categories = list(spending_data['spending_by_category'].keys())

            # Construct prompt for product recommendations
            prompt = f"""Based on the following user data, recommend appropriate financial products:

User Profile:
- Age: {kyc_details.get('Age', 'N/A')}
- Income: ${kyc_details.get('Annual Income (USD)', 'N/A')}
- Employment: {kyc_details.get('Employment Status', 'N/A')}

Spending Patterns:
- Total Spending: ${spending_data.get('total_spend', 0):,.2f}
- Top Categories: {', '.join(spending_categories)}
- Top Merchants: {', '.join(top_merchants)}

User Interests:
{', '.join(user_interests)}

Available Credit Cards:
{json.dumps(credit_cards, indent=2)}

Please provide recommendations in the following JSON format:
{{
    "credit_card_recommendations": [
        {{"card_name": "string", "reason": "string"}}
    ],
    "loan_recommendations": [
        {{"loan_type": "string", "reason": "string"}}
    ],
    "other_recommendations": [
        {{"product_name": "string", "reason": "string"}}
    ]
}}"""

            # Generate recommendations using _generate_response
            content = self._generate_response(prompt, max_tokens=2048)
            
            # Parse JSON response
            try:
                recommendations = json.loads(content)
                return recommendations
            except json.JSONDecodeError as e:
                print(f"\033[91mError parsing JSON response: {str(e)}\033[0m")
                print(f"\033[93mRaw response: {content}\033[0m")
                return {
                    "credit_card_recommendations": [],
                    "loan_recommendations": [],
                    "other_recommendations": []
                }
        except Exception as e:
            print(f"\033[91mError generating recommendations: {str(e)}\033[0m")
            return {
                "credit_card_recommendations": [],
                "loan_recommendations": [],
                "other_recommendations": []
            }
    
    def get_credit_card_recommendations(self, spending_data: Dict[str, Any], kyc_details: Dict[str, Any], user_interests: List[str], available_products: Dict[str, Any]) -> Dict[str, Any]:
        """Generate credit card recommendations based on user data."""
        try:
            # Get top merchants list
            top_merchants = []
            if 'top_merchants' in spending_data:
                top_merchants = [merchant['merchant'] for merchant in spending_data['top_merchants']]

            # Get spending categories
            spending_categories = []
            if 'spending_by_category' in spending_data:
                spending_categories = list(spending_data['spending_by_category'].keys())

            # Construct prompt for credit card recommendations
            prompt = f"""Based on the following user data, recommend appropriate credit cards:

User Profile:
- Age: {kyc_details.get('Age', 'N/A')}
- Income: ${kyc_details.get('Annual Income (USD)', 'N/A')}
- Employment: {kyc_details.get('Employment Status', 'N/A')}

Spending Patterns:
- Total Spending: ${spending_data.get('total_spend', 0):,.2f}
- Top Categories: {', '.join(spending_categories)}
- Top Merchants: {', '.join(top_merchants)}

User Interests:
{', '.join(user_interests)}

Available Credit Cards:
{json.dumps(available_products.get('credit_cards', []), indent=2)}

Please provide recommendations in the following JSON format:
{{
    "recommendations": [
        {{
            "card_name": "string",
            "reason": "string",
            "benefits": ["string"],
            "annual_fee": "string",
            "credit_limit": "string",
            "interest_rate": "string"
        }}
    ]
}}"""

            # Generate recommendations using _generate_response
            content = self._generate_response(prompt, max_tokens=2048)
            
            # Parse JSON response
            try:
                recommendations = json.loads(content)
                return recommendations
            except json.JSONDecodeError as e:
                print(f"\033[91mError parsing JSON response: {str(e)}\033[0m")
                print(f"\033[93mRaw response: {content}\033[0m")
                return {"recommendations": []}
        except Exception as e:
            print(f"\033[91mError generating recommendations: {str(e)}\033[0m")
            return {"recommendations": []}
    
    def analyze_grievances(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze customer grievances from email data."""
        try:
            # Construct prompt for grievance analysis
            prompt = f"""Analyze the following customer grievances and provide insights:

Grievances:
{json.dumps(emails, indent=2)}

Please provide analysis in the following JSON format:
{{
    "common_issues": ["string"],
    "sentiment_analysis": {{
        "positive": "string",
        "negative": "string",
        "neutral": "string"
    }},
    "recommendations": ["string"]
}}"""

            # Generate analysis using _generate_response
            content = self._generate_response(prompt, max_tokens=2048)
            
            # Parse JSON response
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError as e:
                print(f"\033[91mError parsing JSON response: {str(e)}\033[0m")
                print(f"\033[93mRaw response: {content}\033[0m")
                return {
                    "common_issues": [],
                    "sentiment_analysis": {
                        "positive": "",
                        "negative": "",
                        "neutral": ""
                    },
                    "recommendations": []
                }
        except Exception as e:
            print(f"\033[91mError generating analysis: {str(e)}\033[0m")
            return {
                "common_issues": [],
                "sentiment_analysis": {
                    "positive": "",
                    "negative": "",
                    "neutral": ""
                },
                "recommendations": []
            } 