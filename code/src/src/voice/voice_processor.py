from typing import Optional, Tuple, Dict, List, Any
from .audio_transcriber import AudioTranscriber
from .text_to_speech import TextToSpeech
from src.ai.llm_interaction import LLMInteraction
import json
import os
from pathlib import Path
from termcolor import colored
from src.utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

class VoiceProcessor:
    """Voice processing module for handling audio input and output."""
    
    def __init__(self):
        """Initialize the voice processor with necessary components."""
        logger.info("Initializing Voice Processor...")
        
        # Initialize components
        self.transcriber = AudioTranscriber()
        self.tts = TextToSpeech()
        self.llm = LLMInteraction()
        
        # Set up directories
        self.audio_dir = Path("audio")
        self.output_dir = Path("output")
        
        logger.debug("Voice Processor components initialized")
        logger.info("Voice Processor initialized successfully!")

    def load_recommendation_data(self) -> Dict:
        """Load recommendation data from output directory.
        
        Returns:
            Dictionary containing recommendation data
        """
        try:
            data = {}
            output_files = [
                "spending_analysis.json",
                "kyc_details.json",
                "user_interests.json",
                "product_recommendations.json",
                "credit_card_recommendations.json"
            ]
            
            for file in output_files:
                file_path = self.output_dir / file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data[file.replace('.json', '')] = json.load(f)
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading recommendation data: {str(e)}")
            return {}

    def process_query(self, query: str) -> str:
        """Process a text query and generate a response.
        
        Args:
            query: The text query to process
            
        Returns:
            Generated response text
        """
        try:
            # Load data from output directory
            data = self.load_recommendation_data()
            
            # Generate response using LLM
            response = self.llm.generate_response(query, data)
            
            if not response:
                logger.error("Failed to generate response.")
                return ""
                
            logger.info(f"Generated response: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return ""

    def process_audio_file(self, audio_file: str) -> Optional[str]:
        """
        Process an audio file: transcribe, generate response, and convert to speech.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Generated response text or None if processing fails
        """
        logger.info(f"Starting processing of audio file: {audio_file}")
        try:
            # Transcribe audio to text
            logger.debug("Transcribing audio to text")
            transcribed_text = self.transcriber.transcribe_audio(audio_file)
            if not transcribed_text:
                logger.error("Transcription failed")
                return None
            logger.info(f"Transcribed text: {transcribed_text[:100]}...")
            
            # Load user data
            logger.debug("Loading user data")
            data = self._load_user_data()
            if not data:
                logger.error("Failed to load user data")
                return None
                
            # Generate response using LLM
            logger.debug("Generating response using LLM")
            response = self.llm.generate_response(transcribed_text, data)
            if not response:
                logger.error("Failed to generate response")
                return None
            logger.info(f"Generated response: {response[:100]}...")
            
            # Convert response to speech
            logger.debug("Converting response to speech")
            output_file = self._get_output_file(audio_file)
            self.tts.text_to_speech(response, output_file)
            logger.info(f"Response saved as audio: {output_file}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            return None

    def _load_user_data(self) -> Optional[Dict[str, Any]]:
        """Load user data from JSON files."""
        logger.debug("Loading user data from JSON files")
        try:
            data_dir = Path("data")
            
            # Load spending data
            spending_path = data_dir / "spending_data.json"
            logger.debug(f"Loading spending data from {spending_path}")
            with open(spending_path, 'r') as f:
                spending_data = json.load(f)
                
            # Load KYC details
            kyc_path = data_dir / "kyc_details.json"
            logger.debug(f"Loading KYC details from {kyc_path}")
            with open(kyc_path, 'r') as f:
                kyc_details = json.load(f)
                
            # Load credit card recommendations
            credit_path = data_dir / "credit_card_recommendations.json"
            logger.debug(f"Loading credit card recommendations from {credit_path}")
            with open(credit_path, 'r') as f:
                credit_recommendations = json.load(f)
                
            logger.info("Successfully loaded all user data")
            return {
                'spending_data': spending_data,
                'kyc_details': kyc_details,
                'credit_card_recommendations': credit_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
            return None
            
    def _get_output_file(self, input_file: str) -> str:
        """Generate output file path for the audio response."""
        logger.debug("Generating output file path")
        try:
            input_path = Path(input_file)
            output_dir = Path("output/audio")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"response_{input_path.stem}.mp3"
            logger.debug(f"Output file path: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error generating output file path: {str(e)}")
            return "output/audio/response.mp3" 