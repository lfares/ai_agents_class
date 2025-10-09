import openai
import os
import tempfile
import base64
from typing import Optional
from gtts import gTTS
import io

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
        Convert text to speech using OpenAI TTS with Google TTS fallback
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (default: nova - female)
            
        Returns:
            Base64 encoded audio data or None if error
        """
        if not text or not text.strip():
            print("❌ No text provided for TTS")
            return None
        
        # Truncate very long text
        max_length = 4000
        if len(text) > max_length:
            text = text[:max_length] + "..."
            print(f"⚠️ Text truncated to {max_length} characters")
        
        # Try OpenAI TTS first if client is available
        if self.client:
            try:
                print(f"🎤 Trying OpenAI TTS with voice: {voice}")
                print(f"Text length: {len(text)} characters")
                
                response = self.client.audio.speech.create(
                    model=self.model,
                    voice=voice,
                    input=text,
                    response_format="mp3"
                )
                
                audio_data = response.content
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                print(f"✅ OpenAI TTS successful: {len(audio_data)} bytes")
                return audio_base64
                
            except Exception as e:
                print(f"⚠️ OpenAI TTS failed: {e}")
                print("🔄 Falling back to Google TTS...")
        
        # Fallback to Google TTS
        try:
            print(f"🎤 Using Google TTS (free)")
            print(f"Text length: {len(text)} characters")
            
            # Create gTTS object with female voice (default Google voice is female)
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to base64
            audio_data = audio_buffer.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            print(f"✅ Google TTS successful: {len(audio_data)} bytes")
            return audio_base64
            
        except Exception as e:
            print(f"❌ Google TTS also failed: {e}")
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
