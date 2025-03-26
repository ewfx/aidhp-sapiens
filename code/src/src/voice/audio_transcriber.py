import whisper
import numpy as np
import os
from pathlib import Path
import librosa
from termcolor import colored
import warnings
import speech_recognition as sr
from typing import Optional
from src.utils.logger import setup_logger
from pydub import AudioSegment

# Set up logging
logger = setup_logger(__name__)

# Filter specific warnings
warnings.filterwarnings("ignore", message="PySoundFile failed. Trying audioread instead.")
warnings.filterwarnings("ignore", message="librosa.core.audio.__audioread_load")

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="speech_recognition")

class AudioTranscriber:
    """Audio transcription module using Whisper."""
    
    def __init__(self):
        """Initialize the audio transcriber with Whisper model."""
        logger.info("Initializing Whisper model...")
        self.model = whisper.load_model("base")
        self.audio_dir = Path("audio")
        self.recognizer = sr.Recognizer()
        logger.debug("Whisper model initialized successfully!")
        logger.debug("Speech recognizer initialized")
    
    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        logger.info(f"Starting transcription of audio file: {audio_path}")
        try:
            # Load audio using librosa
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                audio, sr = librosa.load(audio_path, sr=16000)
            
            # Transcribe using Whisper
            result = self.model.transcribe(audio, fp16=False)
            text = result["text"].strip()
            
            if not text:
                print(colored("No speech detected in audio file.", "red"))
                return ""
                
            print(colored(f"Transcribed text: {text}", "green"))
            logger.info("Transcription completed successfully")
            return text
            
        except Exception as e:
            print(colored(f"Error during transcription: {str(e)}", "red"))
            logger.error(f"Error during transcription: {str(e)}")
            return ""

    def transcribe_audio(self, audio_file: str) -> Optional[str]:
        """
        Transcribe audio file to text using Google Speech Recognition.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        logger.info(f"Starting transcription of audio file: {audio_file}")
        try:
            # Convert M4A or MP3 to WAV if needed
            audio_path = Path(audio_file)
            if audio_path.suffix.lower() in ['.m4a', '.mp3']:
                logger.debug(f"Converting {audio_path.suffix.upper()} to WAV format")
                wav_file = audio_path.with_suffix('.wav')
                audio = AudioSegment.from_file(audio_file)
                audio.export(wav_file, format="wav")
                audio_file = str(wav_file)
                logger.debug("Conversion completed")
            
            # Load audio file
            logger.debug("Loading audio file")
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                logger.debug("Audio file loaded successfully")
            
            # Perform transcription
            logger.debug("Performing transcription")
            text = self.recognizer.recognize_google(audio)
            logger.info("Transcription completed successfully")
            
            # Clean up temporary WAV file if it was created
            if audio_path.suffix.lower() in ['.m4a', '.mp3'] and wav_file.exists():
                wav_file.unlink()
                logger.debug("Temporary WAV file removed")
            
            return text
            
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from speech recognition service: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return None 