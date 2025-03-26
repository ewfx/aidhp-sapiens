from typing import Dict, Any, List
from pathlib import Path
from llama_cpp import Llama
import json
import pandas as pd
from src.config import LLM_MODEL_PATH
from termcolor import colored
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LLMInteraction:
    def __init__(self):
        """Initialize the LLM interaction with Mistral model."""
        logger.info("Initializing Mistral model...")
        try:
            self.llm = Llama(
                model_path=str(LLM_MODEL_PATH),
                n_ctx=1024,  # Minimal context window
                n_threads=2,  # Minimal threads
                n_gpu_layers=0,  # Disable GPU
                verbose=False,  # Reduce verbosity
                use_mlock=True,  # Lock memory
                use_mmap=False  # Disable memory mapping
            )
            logger.info("Mistral model initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing Mistral model: {str(e)}")
            raise
        
    def _generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using Mistral model."""
        logger.debug(f"Generating response with max_tokens={max_tokens}")
        try:
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
                    logger.debug("Successfully extracted JSON from response")
                    return content[start:end]
                return content
            except Exception as e:
                logger.warning(f"Error extracting JSON from response: {str(e)}")
                return content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
        
    def get_product_recommendations(self, spending_data: Dict[str, Any], kyc_details: Dict[str, Any], user_interests: List[str], available_products: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product recommendations based on user data."""
        logger.info("Generating product recommendations")
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
                logger.debug(f"Processed {len(credit_cards)} credit cards")

            # Get top merchants list
            top_merchants = []
            if 'top_merchants' in spending_data:
                top_merchants = [merchant['merchant'] for merchant in spending_data['top_merchants']]
                logger.debug(f"Found {len(top_merchants)} top merchants")

            # Get spending categories
            spending_categories = []
            if 'spending_by_category' in spending_data:
                spending_categories = list(spending_data['spending_by_category'].keys())
                logger.debug(f"Found {len(spending_categories)} spending categories")

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
            logger.debug("Generating recommendations using LLM")
            content = self._generate_response(prompt, max_tokens=2048)
            
            # Parse JSON response
            try:
                recommendations = json.loads(content)
                logger.info("Successfully generated product recommendations")
                return recommendations
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {str(e)}")
                logger.error(f"Raw response: {content}")
                return {
                    "credit_card_recommendations": [],
                    "loan_recommendations": [],
                    "other_recommendations": []
                }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "credit_card_recommendations": [],
                "loan_recommendations": [],
                "other_recommendations": []
            }
    
    def get_credit_card_recommendations(self, spending_data: Dict[str, Any], kyc_details: Dict[str, Any], user_interests: List[str], available_products: Dict[str, Any]) -> Dict[str, Any]:
        """Generate credit card recommendations based on user data."""
        logger.info("Generating credit card recommendations")
        try:
            # Get top merchants list
            top_merchants = []
            if 'top_merchants' in spending_data:
                top_merchants = [merchant['merchant'] for merchant in spending_data['top_merchants']]
                logger.debug(f"Found {len(top_merchants)} top merchants")

            # Get spending categories
            spending_categories = []
            if 'spending_by_category' in spending_data:
                spending_categories = list(spending_data['spending_by_category'].keys())
                logger.debug(f"Found {len(spending_categories)} spending categories")

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
            logger.debug("Generating credit card recommendations using LLM")
            content = self._generate_response(prompt, max_tokens=2048)
            
            # Parse JSON response
            try:
                recommendations = json.loads(content)
                logger.info("Successfully generated credit card recommendations")
                return recommendations
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {str(e)}")
                logger.error(f"Raw response: {content}")
                return {"recommendations": []}
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {"recommendations": []}
    
    def analyze_grievances(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze customer grievances from email data."""
        logger.info(f"Analyzing {len(emails)} customer grievances")
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
            logger.debug("Generating grievance analysis using LLM")
            content = self._generate_response(prompt, max_tokens=2048)
            
            # Parse JSON response
            try:
                analysis = json.loads(content)
                logger.info("Successfully generated grievance analysis")
                return analysis
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {str(e)}")
                logger.error(f"Raw response: {content}")
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
            logger.error(f"Error generating analysis: {str(e)}")
            return {
                "common_issues": [],
                "sentiment_analysis": {
                    "positive": "",
                    "negative": "",
                    "neutral": ""
                },
                "recommendations": []
            }

    def generate_response(self, query: str, data: dict) -> str:
        """Generate a response based on the query and available data."""
        logger.info(f"Generating response for query: {query[:100]}...")
        try:
            # Extract relevant data
            spending_data = data.get('spending_analysis', {})
            kyc_details = data.get('kyc_details', {})
            credit_cards = data.get('credit_card_recommendations', {}).get('recommendations', [])
            
            # Get top spending categories
            top_categories = dict(sorted(
                spending_data.get('spending_by_category', {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:3])
            
            # Construct prompt for the LLM
            prompt = f"""Based on the user's query and profile, recommend our best products with a persuasive tone:

Query: {query}

Profile:
- Monthly Spend: ${spending_data.get('total_spend', 0):.2f}
- Top Categories: {json.dumps(top_categories)}
- Annual Income: ${kyc_details.get('Annual Income (USD)', 0):,.2f}
- Credit Score: {kyc_details.get('Credit Score', 'Not specified')}

Available Cards:
{json.dumps(credit_cards, indent=2)}

Focus on:
1. Recommend specific cards matching their spending
2. Highlight relevant benefits and rewards
3. Include credit limits and rates
4. Be persuasive but professional"""
            
            # Generate response using LLM
            logger.debug("Generating response using LLM")
            response = self.llm.create_completion(
                prompt,
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
                repeat_penalty=1.1,
                top_k=40
            )
            
            # Extract and clean up the response
            text = response["choices"][0]["text"].strip()
            
            # Try to parse JSON response if present
            if text.startswith('{') and text.endswith('}'):
                try:
                    response_data = json.loads(text)
                    text = response_data.get('response', text)
                    logger.debug("Successfully parsed JSON response")
                except Exception as e:
                    logger.warning(f"Error parsing JSON response: {str(e)}")
            
            logger.info("Successfully generated response")
            return text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "" 