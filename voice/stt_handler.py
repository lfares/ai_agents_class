"""
Speech-to-Text handler using OpenAI Whisper
Note: Whisper is optional for production (Web Speech API is used instead)
"""
import os
import tempfile
from typing import Optional

# Try to import whisper, but don't fail if not available
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper not available. Web Speech API will be used for STT.")

class SpeechToTextHandler:
    """Handle speech-to-text conversion using OpenAI Whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model_size = model_size
        self.model = None
        
        if WHISPER_AVAILABLE:
            self._load_model()
        else:
            print("ℹ️  Whisper not installed. STT features will use Web Speech API only.")
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            # Don't raise - allow app to continue without Whisper
    
    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not WHISPER_AVAILABLE or not self.model:
            raise RuntimeError("Whisper not available. Please use Web Speech API for voice input.")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            print(f"Transcribing audio file: {audio_file_path}")
            
            # Check file size
            file_size = os.path.getsize(audio_file_path)
            print(f"Audio file size: {file_size} bytes")
            
            # Try to transcribe with different options
            result = self.model.transcribe(
                audio_file_path,
                fp16=False,  # Use FP32 for better compatibility
                language='en',  # Specify English for better accuracy
                word_timestamps=False  # Disable word timestamps for faster processing
            )
            
            transcribed_text = result["text"].strip()
            print(f"✅ Transcription completed: {len(transcribed_text)} characters")
            print(f"Transcribed text: {transcribed_text[:100]}...")
            
            return transcribed_text
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def transcribe_audio_data(self, audio_data: bytes) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Transcribed text
        """
        if not WHISPER_AVAILABLE or not self.model:
            raise RuntimeError("Whisper not available. Please use Web Speech API for voice input.")
        
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe the temporary file
            result = self.transcribe_audio_file(temp_file_path)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return result
        except Exception as e:
            print(f"❌ Error transcribing audio data: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "is_loaded": self.model is not None,
            "whisper_available": WHISPER_AVAILABLE
        }
    
    def is_available(self) -> bool:
        """Check if Whisper STT is available"""
        return WHISPER_AVAILABLE and self.model is not None
