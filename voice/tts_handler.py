import openai
import os
import tempfile
import base64
from typing import Optional

class TextToSpeechHandler:
    def __init__(self):
        """Initialize TTS handler with OpenAI TTS API"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for TTS functionality")
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
            print("✅ OpenAI TTS client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing OpenAI TTS client: {e}")
            raise
        
        self.voice = "nova"  # Female voice option
        self.model = "tts-1"  # Fast model for real-time use
        
    def get_available_voices(self):
        """Get list of available voices"""
        return {
            "nova": "Female, warm and friendly",
            "alloy": "Neutral, clear and professional", 
            "echo": "Male, warm and expressive",
            "fable": "Male, deep and authoritative",
            "onyx": "Male, deep and smooth",
            "shimmer": "Female, soft and gentle"
        }
    
    def text_to_speech(self, text: str, voice: str = "nova") -> Optional[str]:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (default: nova - female)
            
        Returns:
            Base64 encoded audio data or None if error
        """
        if not self.client:
            print("❌ TTS client not available")
            return None
            
        if not text or not text.strip():
            print("❌ No text provided for TTS")
            return None
            
        try:
            print(f"🎤 Converting text to speech with voice: {voice}")
            print(f"Text length: {len(text)} characters")
            
            # Truncate very long text to avoid API limits
            max_length = 4000  # OpenAI TTS limit
            if len(text) > max_length:
                text = text[:max_length] + "..."
                print(f"⚠️ Text truncated to {max_length} characters")
            
            # Generate speech
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            # Convert to base64 for web transmission
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            print(f"✅ TTS conversion successful: {len(audio_data)} bytes")
            return audio_base64
            
        except Exception as e:
            print(f"❌ Error in TTS conversion: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_voice_info(self):
        """Get information about current voice configuration"""
        return {
            "current_voice": self.voice,
            "model": self.model,
            "available_voices": self.get_available_voices()
        }
