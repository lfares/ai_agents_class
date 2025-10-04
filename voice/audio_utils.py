"""
Audio utilities for voice processing
"""
import pyaudio
import wave
import os
import tempfile
from typing import Optional

class AudioRecorder:
    """Simple audio recorder for capturing voice input"""
    
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stream = None
    
    def start_recording(self):
        """Start recording audio"""
        self.frames = []
        self.is_recording = True
        
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
    
    def stop_recording(self) -> str:
        """Stop recording and save to temporary file"""
        if not self.is_recording or not self.stream:
            return None
            
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        # Save audio data
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        return temp_file.name
    
    def record_audio(self, duration: int = 5) -> str:
        """Record audio for specified duration in seconds"""
        self.start_recording()
        
        # Record for specified duration
        for _ in range(0, int(self.rate / self.chunk * duration)):
            if self.is_recording:
                data = self.stream.read(self.chunk)
                self.frames.append(data)
        
        return self.stop_recording()
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()
