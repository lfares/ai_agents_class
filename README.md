# AI Agents Class
MIT MAS.665 class work on AI Agents and the Agentic Web.

## Overview
This project provides AI agents with voice capabilities to help with:
1. **Job Interview Preparation** - Generate interview questions and answers based on CV and job description
2. **PDF Reading Summarization** - Summarize academic readings and create Excel files with key concepts

## Features
- 🤖 **Interview Helper Agent** - Prepares interview questions and answers in your voice
- 📚 **Reading Summarizer Agent** - Summarizes PDF readings with focus on your interests
- 🎤 **Speech-to-Text** - Voice input for job descriptions and custom focus areas
- 🔊 **Text-to-Speech** - Listen to agent responses with natural voice output
- 🏷️ **Dynamic Focus Areas** - Add/remove interests interactively with voice or text
- 🔧 **Multi-LLM Support** - Works with both OpenAI and Google Gemini models
- 📊 **Excel Output** - Automatically creates structured Excel files from summaries
- 📄 **PDF Processing** - Converts PDFs to text for analysis
- 🌐 **Web Interface** - Beautiful, modern UI with real-time updates

## Local Setup

### 1. Create Environment File
Create a `.env` file with your API credentials:

```bash
# For OpenAI (default)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
LLM_TYPE=openai

# For Google Gemini (optional)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
LLM_TYPE=gemini
```

### 2. Create Virtual Environment (Python 3.12)
```bash
python3.12 -m venv venv312
source venv312/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies (for Voice Features)

**For macOS:**
```bash
# Required for Speech-to-Text (Whisper)
brew install portaudio ffmpeg
```

**For Linux:**
```bash
sudo apt-get install portaudio19-dev ffmpeg
```

**For Windows:**
- Install FFmpeg from https://ffmpeg.org/download.html
- Add FFmpeg to your system PATH

### 5. Set Environment Variables
```bash
# Required for LLM and Text-to-Speech functionality
export OPENAI_API_KEY=your_openai_api_key_here

# Optional: For chat completions
export OPENAI_MODEL=gpt-3.5-turbo

# Optional: For Gemini LLM
export GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Prepare Your Files
- **CV File**: Place your CV data in `resources/cv.json` (JSON format)
- **PDF File**: Place any PDF reading in `resources/example_reading.pdf` (optional)

### 7. Run the Web Application
```bash
python app.py
```

The application will be available at `http://localhost:5002`

## Usage

### Web Interface (Recommended)
Access the modern web interface at `http://localhost:5002` with two main agents:

#### 1. Interview Helper Agent
**Text Input:**
- Enter job description in the text area
- Click "Prepare Interview" to generate questions and answers

**Voice Input:**
- Click the microphone button (🎤) next to the job description field
- Speak your job description naturally
- Text appears in real-time as you speak
- Click "Stop" when finished

**Voice Output:**
- After receiving interview preparation results
- Click the "Read Aloud" button to hear the response
- Features natural female voice (Google TTS fallback if OpenAI quota exceeded)
- Click again to stop playback

#### 2. PDF Reading Summarizer Agent
**Upload PDF:**
- Click "Choose File" and select your PDF reading
- Or drag and drop the file

**Manage Focus Areas:**
- **View Default Tags**: AI in Education, Marginalized Communities, EdTech, etc.
- **Remove Tags**: Click any tag with an × to remove it
- **Add New Tags (Text)**: Type in the input box and click "+ Add"
- **Add New Tags (Voice)**: Click the microphone button (🎤), speak the focus area, then click "+ Add"

**Generate Summary:**
- Click "Summarize PDF" to analyze the reading
- Agent generates a structured table with key concepts and relevance
- Click "Read Aloud" to hear the summary
- Download Excel file with the summary data

### Command Line Interface (Alternative)
```bash
python main.py
```

#### Interview Preparation
1. Run the application
2. Enter your job description (or use the default)
3. The Interview Helper agent will generate:
   - Potential interview questions
   - Answers in your voice using STAR method
   - Tips for confidence and preparation

#### PDF Summarization
1. Run the application
2. Choose "y" when asked about PDF summarization
3. Provide the PDF file path (default: `resources/example_reading.pdf`)
4. Specify Excel output path (default: `uploads/reading_summary.xlsx`)
5. The Reading Summarizer agent will:
   - Read and analyze the PDF content
   - Extract key concepts relevant to your interests
   - Create an Excel file with structured summary

## Configuration

### LLM Selection
- **OpenAI**: Set `LLM_TYPE=openai` in `.env`
- **Gemini**: Set `LLM_TYPE=gemini` in `.env`

### Voice Features
**Speech-to-Text (STT):**
- Uses OpenAI Whisper for offline transcription
- Web Speech API for real-time voice input in the browser
- Supports English language by default
- Works on Chrome, Edge, and Safari (with limitations)

**Text-to-Speech (TTS):**
- Primary: OpenAI TTS API with female voice (nova)
- Fallback: Google TTS (gTTS) - free, no API key required
- Automatic fallback if OpenAI quota exceeded
- Natural, conversational voice output

### Focus Areas (for PDF summarization)
**Default interests** (can be customized via web interface):
- AI in Education
- Marginalized Communities
- EdTech
- Learning Design
- Career Readiness
- K-12 Education
- Soft Skills

**Custom interests**: Add your own via text or voice input in the web interface

## File Structure
```
├── main.py                 # Command-line application
├── app.py                  # Flask web application
├── requirements.txt        # Python dependencies
├── resources/              # Resource files
│   ├── cv.json            # Your CV data (JSON format)
│   └── example_reading.pdf # Sample PDF for testing
├── uploads/                # Uploaded files and generated outputs
│   └── *.xlsx             # Generated Excel summaries
├── voice/                  # Voice processing modules
│   ├── __init__.py        # Module initialization
│   ├── stt_handler.py     # Speech-to-Text handler (Whisper)
│   ├── tts_handler.py     # Text-to-Speech handler (OpenAI TTS + gTTS)
│   └── audio_utils.py     # Audio utility functions
├── static/                 # Web application static files
│   ├── css/
│   │   └── style.css      # Styles and animations
│   └── js/
│       └── app.js         # Frontend logic and voice features
├── templates/              # Web application templates
│   └── index.html         # Main web interface
├── docs/                   # Documentation
│   ├── DEPLOYMENT.md      # Deployment instructions
│   ├── LEARNINGS.md       # Project learnings
│   └── WEB_SETUP.md       # Web setup guide
├── config/                 # Configuration files
│   ├── Procfile           # Heroku deployment config
│   ├── runtime.txt        # Python runtime version
│   └── .env.example       # Environment variables template
└── .env                   # API keys and configuration
```

## Dependencies

### Core AI & Agent Framework
- `crewai` - AI agent framework
- `langchain-google-genai` - Gemini LLM integration
- `openai` - OpenAI API for LLM and TTS

### Voice Processing
- `openai-whisper` - Speech-to-Text (Whisper model)
- `gtts` - Google Text-to-Speech (fallback)
- `pyaudio` - Audio input/output handling

### Document Processing
- `pypdf` - PDF text extraction
- `pandas` - Data manipulation
- `openpyxl` - Excel file creation

### Web Application
- `flask` - Web framework
- `werkzeug` - WSGI utilities

### Utilities
- `python-dotenv` - Environment variables
- `ffmpeg` - Audio format conversion (system dependency)

## Troubleshooting

### Python Version Issues
If you get Python version errors, make sure you're using Python 3.12:
```bash
python3.12 --version
```

### API Key Issues
- Check your `.env` file has the correct API keys
- Verify your API keys are valid and have sufficient quota
- For Gemini, ensure `GEMINI_API_KEY` is set in your environment
- For OpenAI TTS, ensure `OPENAI_API_KEY` is set (falls back to Google TTS if missing)

### Voice Feature Issues

**Speech-to-Text not working:**
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check microphone permissions in your browser
- For macOS: System Preferences → Security & Privacy → Microphone
- Whisper model downloads automatically on first use (~140MB for base model)

**Text-to-Speech not working:**
- If OpenAI TTS fails, system automatically falls back to Google TTS
- Google TTS requires internet connection but no API key
- Check browser console for detailed error messages

**Audio issues:**
- Ensure PortAudio is installed: `brew list portaudio` (macOS)
- Check system audio settings and permissions
- Try refreshing the browser page

### PDF Reading Issues
- Ensure the PDF file exists and is readable
- The system will create a temporary text file for processing
- Check file permissions in your directory
- Large PDFs may take longer to process

### Browser Compatibility
- **Recommended**: Chrome or Edge for full voice feature support
- **Safari**: Limited Web Speech API support
- **Firefox**: No Web Speech API support (voice features disabled)

## Example Output
- **Interview Preparation**: Structured Q&A with STAR method answers, voice playback available
- **PDF Summary**: Interactive table with key concepts and relevance, Excel download, voice playback
- **Focus Areas**: Dynamic tag system with add/remove capabilities via text or voice