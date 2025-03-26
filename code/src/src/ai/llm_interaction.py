from typing import Dict, Any, List
from pathlib import Path
from llama_cpp import Llama
import json
import pandas as pd
from config.config import LLM_MODEL_PATH
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
                n_ctx=4096,  # Increased context window
                n_threads=4,  # Increased threads
                n_gpu_layers=0,  # Disable GPU
                verbose=True,  # Enable verbosity for debugging
                use_mlock=True,  # Lock memory
                use_mmap=True  # Enable memory mapping
            )
            logger.info("Mistral model initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing Mistral model: {str(e)}")
            raise
        
    def _generate_response(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate response using Mistral model."""
        logger.debug(f"Generating response with max_tokens={max_tokens}")
        try:
            # Add system message to guide the model
            system_message = "You are a helpful AI assistant that provides recommendations in JSON format. Always respond with valid JSON."
            full_prompt = f"{system_message}\n\n{prompt}"
            
            response = self.llm(
                full_prompt,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more consistent output
                top_p=0.9,
                echo=False,
                stop=["</s>", "Human:", "Assistant:"],
                repeat_penalty=1.1  # Add repeat penalty to avoid loops
            )
            content = response['choices'][0]['text'].strip()
            
            # Extract JSON from the response if it contains text before/after
            try:
                # Find the first '{' and last '}'
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    # Validate JSON before returning
                    json.loads(json_str)
                    logger.debug("Successfully extracted and validated JSON from response")
                    return json_str
                return content
            except json.JSONDecodeError as e:
                logger.warning(f"Error extracting/validating JSON from response: {str(e)}")
                return content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
        
    def get_product_recommendations(self, spending_data: Dict[str, Any], kyc_details: Dict[str, Any], user_interests: List[str], available_products: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product recommendations based on user data."""
        logger.info("Generating product recommendations")
        try:
            # Get user behavior insights
            behavior_insights = []
            if 'spending_by_category' in spending_data:
                top_category = spending_data.get('max_spending_category', '')
                behavior_insights.append(f"Your highest spending category is {top_category}")
            
            if 'average_transaction_amount' in spending_data:
                behavior_insights.append(f"Your average transaction amount is ${float(spending_data['average_transaction_amount']):.2f}")
            
            # Calculate average monthly spending from monthly_spending data
            if 'monthly_spending' in spending_data:
                monthly_values = list(spending_data['monthly_spending'].values())
                avg_monthly_spend = sum(monthly_values) / len(monthly_values) if monthly_values else 0
                behavior_insights.append(f"Your average monthly spending is ${float(avg_monthly_spend):.2f}")

            # Get top merchants list
            top_merchants = []
            if 'top_merchants_by_spend' in spending_data:
                top_merchants = list(spending_data['top_merchants_by_spend'].keys())
                logger.debug(f"Found {len(top_merchants)} top merchants")

            # Get spending categories
            spending_categories = []
            if 'spending_by_category' in spending_data:
                spending_categories = list(spending_data['spending_by_category'].keys())
                logger.debug(f"Found {len(spending_categories)} spending categories")

            # Construct prompt for product recommendations
            prompt = f"""Based on the following user data, recommend appropriate Wells Fargo financial products:

User Profile:
- Age: {kyc_details.get('Age', 'N/A')}
- Income: ${float(kyc_details.get('Annual Income (USD)', 0)):,.2f}
- Employment: {kyc_details.get('Employment Status', 'N/A')}
- Credit Score: {kyc_details.get('Credit Score', 'N/A')}
- Location: {kyc_details.get('City', 'N/A')}, {kyc_details.get('State', 'N/A')}

Spending Patterns:
- Total Spending: ${float(spending_data.get('total_spend', 0)):,.2f}
- Top Categories: {', '.join(spending_categories)}
- Top Merchants: {', '.join(top_merchants)}

User Behavior Insights:
{chr(10).join(behavior_insights)}

User Interests:
{', '.join(user_interests)}

Available Wells Fargo Products:
Credit Cards:
{pd.read_csv('data/Wells_Fargo_Credit_Card_Details.csv').to_json(orient='records', indent=2)}

Loans:
{pd.read_csv('data/Wells_Fargo_Loan_Details.csv').to_json(orient='records', indent=2)}

Please provide recommendations in the following JSON format:
{{
    "credit_card_recommendations": [
        {{
            "card_name": "string",
            "reason": "string",
            "user_behavior_match": "string"
        }}
    ],
    "loan_recommendations": [
        {{
            "loan_type": "string",
            "reason": "string",
            "user_behavior_match": "string"
        }}
    ],
    "other_recommendations": [
        {{
            "product_name": "string",
            "reason": "string",
            "user_behavior_match": "string"
        }}
    ]
}}

Important:
1. Only recommend Wells Fargo products from the available_products list
2. Include specific user behavior analysis in the reason and user_behavior_match fields
3. Focus on how the product's benefits align with the user's spending patterns and interests"""

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
            # Get spending categories
            spending_categories = []
            if 'spending_by_category' in spending_data:
                spending_categories = list(spending_data['spending_by_category'].keys())
                logger.debug(f"Found {len(spending_categories)} spending categories")

            # Get user behavior insights
            behavior_insights = []
            if 'spending_by_category' in spending_data:
                top_category = spending_data.get('max_spending_category', '')
                behavior_insights.append(f"Your highest spending category is {top_category}")
            
            if 'average_transaction_amount' in spending_data:
                behavior_insights.append(f"Your average transaction amount is ${float(spending_data['average_transaction_amount']):.2f}")
            
            # Calculate average monthly spending from monthly_spending data
            if 'monthly_spending' in spending_data:
                monthly_values = list(spending_data['monthly_spending'].values())
                avg_monthly_spend = sum(monthly_values) / len(monthly_values) if monthly_values else 0
                behavior_insights.append(f"Your average monthly spending is ${float(avg_monthly_spend):.2f}")

            # Get top merchants list
            top_merchants = []
            if 'top_merchants_by_spend' in spending_data:
                top_merchants = list(spending_data['top_merchants_by_spend'].keys())
                logger.debug(f"Found {len(top_merchants)} top merchants")

            # Construct prompt for credit card recommendations
            prompt = f"""Based on the following user data, recommend appropriate Wells Fargo credit cards:

User Profile:
- Age: {kyc_details.get('Age', 'N/A')}
- Income: ${float(kyc_details.get('Annual Income (USD)', 0)):,.2f}
- Employment: {kyc_details.get('Employment Status', 'N/A')}
- Credit Score: {kyc_details.get('Credit Score', 'N/A')}
- Location: {kyc_details.get('City', 'N/A')}, {kyc_details.get('State', 'N/A')}

Spending Patterns:
- Total Spending: ${float(spending_data.get('total_spend', 0)):,.2f}
- Top Categories: {', '.join(spending_categories)}
- Top Merchants: {', '.join(top_merchants)}

User Behavior Insights:
{chr(10).join(behavior_insights)}

User Interests:
{', '.join(user_interests)}

Available Wells Fargo Credit Cards:
{pd.read_csv('data/Wells_Fargo_Credit_Card_Details.csv').to_json(orient='records', indent=2)}

Please provide recommendations in the following JSON format:
{{
    "recommendations": [
        {{
            "card_name": "string",
            "reason": "string",
            "benefits": ["string"],
            "annual_fee": "string",
            "credit_limit": "string",
            "interest_rate": "string",
            "user_behavior_match": "string"
        }}
    ]
}}

Important:
1. Only recommend Wells Fargo credit cards from the available list
2. Include specific user behavior analysis in the reason and user_behavior_match fields
3. Focus on how the card's benefits align with the user's spending patterns and interests"""

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