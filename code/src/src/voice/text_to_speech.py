from gtts import gTTS
from pathlib import Path
from typing import Optional
from src.utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

class TextToSpeech:
    """Text-to-speech module using Google Text-to-Speech."""
    
    def __init__(self):
        """Initialize the text-to-speech converter."""
        logger.info("Initializing TextToSpeech")
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Output directory created")
    
    def text_to_speech(self, text: str, output_file: str) -> Optional[str]:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file
            
        Returns:
            Path to the saved audio file or None if conversion fails
        """
        logger.info(f"Converting text to speech: {text[:100]}...")
        try:
            # Create gTTS object
            logger.debug("Creating gTTS object")
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save audio file
            logger.debug(f"Saving audio file to {output_file}")
            tts.save(output_file)
            logger.info(f"Audio file saved successfully: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            return None 