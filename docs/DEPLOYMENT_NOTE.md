# Deployment Note: Voice Features

## Production Configuration

### Why Whisper is Disabled in Production

The production deployment (Railway) **intentionally does not include** OpenAI Whisper and PyAudio dependencies because:

1. **System Dependencies Required**: 
   - PyAudio requires PortAudio (system-level library)
   - Whisper requires FFmpeg for audio processing
   - These add complexity and build time to deployments

2. **Web Speech API is Used Instead**:
   - All voice input in the web interface uses Web Speech API
   - Runs entirely in the browser (Chrome/Edge)
   - Zero latency, no backend processing needed
   - No API costs

3. **Whisper Was for Development Only**:
   - Used during development for testing
   - Provided fallback option for recorded audio
   - Not needed for production web interface

### Voice Features in Production

✅ **Available:**
- **Speech-to-Text**: Web Speech API (browser-based, real-time)
- **Text-to-Speech**: 
  - Primary: OpenAI TTS (requires `OPENAI_API_KEY`)
  - Fallback: Google TTS (gTTS) - always available, free

❌ **Not Available:**
- **Whisper STT**: Not needed (Web Speech API is superior for real-time use)
- **PyAudio**: Not needed (no audio recording on backend)

### Dependencies for Deployment

**Required (in `requirements.txt`):**
```
Flask==3.1.2
Werkzeug==3.1.3
crewai==0.186.1
gtts==2.5.4  # Google TTS fallback
# ... other core dependencies
```

**Not Required (commented out):**
```
# openai-whisper==20250625  # Only for local development
# pyaudio==0.2.14           # Requires system dependencies
# ffmpeg-python==0.2.0      # Only needed for Whisper
```

### Local Development

For **local development**, if you want to use Whisper:

1. **Install System Dependencies:**
   ```bash
   # macOS
   brew install portaudio ffmpeg
   
   # Linux
   sudo apt-get install portaudio19-dev ffmpeg
   ```

2. **Uncomment in `requirements.txt`:**
   ```
   openai-whisper==20250625
   pyaudio==0.2.14
   ffmpeg-python==0.2.0
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Error Handling

The application **gracefully handles** missing Whisper:

```python
# voice/stt_handler.py
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper not available. Web Speech API will be used for STT.")
```

If Whisper is not installed:
- App continues to run normally
- Voice input still works via Web Speech API
- `/api/voice-status` returns `whisper_available: false`
- Frontend gracefully uses Web Speech API only

### Testing Deployment Locally

To test without Whisper (simulating production):

```bash
# 1. Comment out Whisper dependencies in requirements.txt
# (already done by default)

# 2. Create fresh virtual environment
python3.12 -m venv venv_test
source venv_test/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python app.py

# 5. Test voice features in browser
# - Voice input should work (Web Speech API)
# - Voice output should work (gTTS fallback)
```

### Deployment Checklist

When deploying to Railway/Heroku/etc:

- ✅ Keep Whisper dependencies commented out
- ✅ Ensure `gtts` is installed (TTS fallback)
- ✅ Set `OPENAI_API_KEY` environment variable (optional, for better TTS)
- ✅ Set `GEMINI_API_KEY` environment variable (for LLM)
- ✅ Verify Web Speech API works in target browsers
- ✅ Test voice features work without Whisper

### Browser Compatibility

**Production voice features work in:**
- ✅ Chrome (best support)
- ✅ Edge (full support)
- ⚠️ Safari (limited Web Speech API support)
- ❌ Firefox (no Web Speech API)

### Cost in Production

**With this configuration:**
- STT: **$0** (Web Speech API is free)
- TTS: **$0** (gTTS fallback is free, or ~$15/1M chars for OpenAI)
- Total: **$0-15/1M characters** depending on OpenAI usage

**Why this is optimal:**
- Free STT (browser-based)
- Free TTS fallback (no API quota issues)
- Optional premium TTS (better quality when available)
- No deployment complexity (no system dependencies)

### Troubleshooting Production Issues

**If voice input doesn't work:**
1. Check browser console for errors
2. Verify browser supports Web Speech API
3. Check microphone permissions
4. Try Chrome/Edge instead of Firefox/Safari

**If voice output doesn't work:**
1. Check `/api/voice-status` endpoint
2. Verify gTTS is installed: `pip list | grep gtts`
3. Check internet connection (gTTS needs it)
4. Review server logs for TTS errors

**If deployment fails:**
1. Ensure Whisper/PyAudio are commented out in `requirements.txt`
2. Check Railway logs for specific errors
3. Verify Python version is 3.10+ (we use 3.12)
4. Test locally first with clean virtual environment

---

## Summary

The production deployment is **intentionally streamlined** to exclude Whisper because:
- Web Speech API provides better real-time experience
- Removes complex system dependencies
- Reduces deployment complexity and build time
- No loss of functionality for web users
- Cost optimization (everything free except optional OpenAI TTS)

This architecture provides **100% voice feature availability** in production while keeping deployment simple and costs low.

