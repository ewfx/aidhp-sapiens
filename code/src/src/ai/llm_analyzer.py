from typing import Dict, List, Any
import os
from pathlib import Path
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer

class LLMAnalyzer:
    def __init__(self):
        """Initialize the LLM analyzer with local Mistral model."""
        self.model_path = Path("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        
        # Create models directory if it doesn't exist
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download model if it doesn't exist
        if not self.model_path.exists():
            print("Downloading Mistral model...")
            import huggingface_hub
            huggingface_hub.hf_hub_download(
                "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                local_dir=self.model_path.parent
            )
        
        # Initialize the model
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=2048,  # Context window
            n_threads=4,  # Number of CPU threads to use
            n_gpu_layers=0  # CPU only for now
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def _generate_prompt(self, analysis_type: str, data: Dict[str, Any]) -> str:
        """Generate appropriate prompt based on analysis type."""
        if analysis_type == "insights":
            return f"""Based on the following financial analysis, provide personalized insights and recommendations:

Spending Patterns:
{data['spending_patterns']}

Credit Score Factors:
{data['credit_factors']}

Savings Recommendations:
{data['savings_recommendations']}

Credit Card Usage:
{data['credit_card_usage']}

Please provide:
1. Key financial insights
2. Personalized recommendations
3. Action items for improvement
4. Risk factors to watch out for

Format your response in a clear, structured manner."""

        elif analysis_type == "email":
            return f"""Based on the following financial analysis and insights, draft a personalized email to the customer:

Financial Analysis:
{data['insights']}

Please draft a professional, friendly email that:
1. Highlights key findings
2. Provides actionable recommendations
3. Encourages engagement with financial services
4. Maintains a supportive and encouraging tone

Format the email with appropriate greeting and closing."""

    def generate_financial_insights(
        self,
        spending_patterns: Dict[str, Any],
        credit_factors: Dict[str, Any],
        savings_recommendations: List[Dict[str, Any]],
        credit_card_usage: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate personalized financial insights using local LLM."""
        data = {
            'spending_patterns': spending_patterns,
            'credit_factors': credit_factors,
            'savings_recommendations': savings_recommendations,
            'credit_card_usage': credit_card_usage
        }
        
        prompt = self._generate_prompt("insights", data)
        
        # Generate response using local model
        response = self.llm(
            prompt,
            max_tokens=1024,
            temperature=0.7,
            stop=["###"],
            echo=False
        )
        
        # Parse and structure the response
        insights = {
            'key_insights': response['choices'][0]['text'].strip(),
            'recommendations': response['choices'][0]['text'].strip(),
            'action_items': response['choices'][0]['text'].strip(),
            'risk_factors': response['choices'][0]['text'].strip()
        }
        
        return insights
    
    def generate_email_draft(self, insights: Dict[str, str]) -> str:
        """Generate personalized email draft using local LLM."""
        data = {'insights': insights}
        prompt = self._generate_prompt("email", data)
        
        # Generate response using local model
        response = self.llm(
            prompt,
            max_tokens=1024,
            temperature=0.7,
            stop=["###"],
            echo=False
        )
        
        return response['choices'][0]['text'].strip() 