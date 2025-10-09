# Web Platform Setup Guide

## Overview
This guide will help you set up and run the AI Agent Assistant web platform locally.

## Prerequisites
- Python 3.12
- Virtual environment (venv312)
- API keys (OpenAI or Gemini)
- System dependencies: FFmpeg, PortAudio (for voice features)

## Quick Start

### 1. Install System Dependencies (for Voice Features)

**For macOS:**
```bash
brew install portaudio ffmpeg
```

**For Linux:**
```bash
sudo apt-get install portaudio19-dev ffmpeg
```

### 2. Install Python Dependencies
```bash
# Activate your virtual environment
source venv312/bin/activate

# Install all dependencies (includes Flask, voice processing, etc.)
pip install -r requirements.txt
```

### 3. Start the Web Server
```bash
# Run the Flask application
python app.py
```

### 4. Access the Platform
Open your browser and go to: `http://localhost:5002`

## Features

### 🎨 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Beautiful UI**: Modern gradient design with smooth animations
- **Interactive Elements**: Drag & drop file uploads, real-time feedback

### 🎤 Voice Capabilities
- **Speech-to-Text**: Voice input for job descriptions and custom focus areas
- **Text-to-Speech**: Listen to agent responses with natural voice
- **Real-time Transcription**: See text appear as you speak
- **Automatic Fallback**: Google TTS when OpenAI quota exceeded

### 🤖 Two AI Agents
1. **Interview Helper**: Generate interview questions and answers
2. **Reading Summarizer**: Summarize PDFs and create Excel reports

### 📱 User Experience
- **Voice Input**: Click microphone buttons to speak instead of type
- **Voice Output**: Click "Read Aloud" to hear agent responses
- **Dynamic Focus Areas**: Add/remove interests with text or voice
- **File Upload**: Drag & drop or click to upload PDFs
- **Real-time Processing**: Live loading indicators and progress feedback
- **Download Results**: Direct download links for generated Excel files
- **Error Handling**: Clear error messages and notifications

## Usage

### Interview Preparation
**Text Input:**
1. Navigate to the Interview Helper section
2. Type or paste the job description in the text area
3. Click "Prepare Interview" to generate questions and answers

**Voice Input:**
1. Click the 🎤 microphone button next to the job description field
2. Speak the job description naturally
3. Text appears in real-time as you speak
4. Click "Stop" when finished
5. Click "Prepare Interview"

**Voice Output:**
1. After receiving results, click "Read Aloud" button
2. Listen to the interview preparation with natural voice
3. Click again to stop playback

### PDF Summarization
**Upload and Customize:**
1. Click "Choose File" to select a PDF or drag & drop
2. Review default focus areas (tags shown)
3. Remove unwanted tags by clicking them
4. Add custom focus areas:
   - Type in the input box and click "+ Add", OR
   - Click 🎤 microphone, speak the focus area, then click "+ Add"

**Generate and Listen:**
1. Click "Summarize PDF"
2. View the structured summary table
3. Click "Read Aloud" to hear the summary
4. Download Excel file with detailed summary

## File Structure
```
├── app.py                 # Flask web application
├── main.py                # Command-line agent functions
├── voice/                 # Voice processing modules
│   ├── stt_handler.py    # Speech-to-Text (Whisper)
│   ├── tts_handler.py    # Text-to-Speech (OpenAI + gTTS)
│   └── audio_utils.py    # Audio utilities
├── templates/
│   └── index.html        # Main web page with voice UI
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling + voice animations
│   └── js/
│       └── app.js        # Interactive functionality + voice features
├── uploads/              # Temporary file storage
├── resources/            # CV and example files
└── requirements.txt      # All dependencies
```

## API Endpoints

### Interview Preparation
- **POST** `/api/interview`
- **Body**: `{"cv_text": "...", "job_description": "..."}`
- **Response**: Interview preparation text

### PDF Summarization
- **POST** `/api/summarize`
- **Body**: Form data with PDF file and custom_interests
- **Response**: Summary text and Excel file download link

### Voice Features
- **POST** `/api/transcribe`
- **Body**: Form data with audio file (WebM/WAV)
- **Response**: `{"transcription": "..."}`

- **POST** `/api/text-to-speech`
- **Body**: `{"text": "..."}`
- **Response**: `{"audio_base64": "...", "format": "mp3"}`

- **GET** `/api/voice-status`
- **Response**: Voice feature availability status

### File Download
- **GET** `/api/download/<filename>`
- **Response**: File download

### Health Check
- **GET** `/api/health`
- **Response**: Server status

## Configuration

### Environment Variables
The web platform uses the same `.env` file as the command-line version:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
LLM_TYPE=openai

# Gemini Configuration (alternative)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
LLM_TYPE=gemini
```

### File Upload Limits
- **Maximum file size**: 16MB
- **Allowed formats**: PDF, JSON
- **Upload directory**: `uploads/` (auto-created)

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# If port 5002 is busy, change it in app.py
app.run(debug=True, host='0.0.0.0', port=5003)
```

#### 2. Voice Features Not Working

**Speech-to-Text Issues:**
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check browser microphone permissions
- Try Chrome or Edge (best compatibility)
- Whisper model downloads on first use (~140MB)

**Text-to-Speech Issues:**
- System automatically falls back to Google TTS if OpenAI fails
- Check browser console for detailed error messages
- Ensure internet connection for Google TTS
- Verify audio output device is working

#### 3. File Upload Errors
- Check file size (max 16MB)
- Ensure file format is PDF
- Verify upload directory permissions
- Check disk space

#### 4. API Key Issues
- Verify your `.env` file has correct API keys
- Check API key quotas and billing
- Ensure environment variables are loaded
- OpenAI TTS will fallback to Google TTS if quota exceeded

#### 5. Agent Errors
- Check that all dependencies are installed
- Verify your `resources/cv.json` file exists
- Ensure PDF files are readable
- Check terminal logs for detailed error messages

#### 6. Browser Compatibility
- **Best**: Chrome, Edge (full support)
- **Limited**: Safari (Web Speech API limitations)
- **Not Supported**: Firefox (no Web Speech API)

### Debug Mode
The Flask app runs in debug mode by default, which provides:
- Automatic reloading on code changes
- Detailed error messages
- Interactive debugger

## Security Notes

### Development Only
This setup is for local development. For production:
- Change the secret key in `app.py`
- Use a production WSGI server (gunicorn)
- Implement proper authentication
- Add rate limiting
- Use HTTPS

### File Handling
- Uploaded files are stored temporarily
- Files are automatically cleaned up
- No persistent file storage

## Customization

### Styling
Edit `static/css/style.css` to customize:
- Colors and gradients
- Fonts and typography
- Layout and spacing
- Animations and transitions

### Functionality
Edit `static/js/app.js` to add:
- New form validations
- Additional file formats
- Custom notifications
- Enhanced user interactions

## Support
For issues or questions:
1. Check the console for error messages
2. Verify all dependencies are installed
3. Ensure API keys are valid
4. Check file permissions and paths
