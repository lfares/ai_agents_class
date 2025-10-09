"""
Flask Web Application for AI Agent Assistant
Provides a web interface for interview preparation and PDF summarization
"""

import os
import json
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from crewai import Task
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# Import voice processing modules
from voice.stt_handler import SpeechToTextHandler
from voice.tts_handler import TextToSpeechHandler

# Import our existing agent functions
from main import (
    create_interviewer_agent,
    create_reading_summary_agent,
    create_interview_task,
    create_reading_summary_task,
    convert_pdf_to_text,
    create_excel_from_summary,
    INTERESTS
)
from crewai import Crew, Process

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'json'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple Mock LLM for testing
class MockLLM:
    def __init__(self):
        self.model_name = "mock-llm"
    
    def invoke(self, messages, **kwargs):
        # Simple mock response based on the task
        if isinstance(messages, list) and len(messages) > 0:
            content = str(messages[-1].content) if hasattr(messages[-1], 'content') else str(messages[-1])
            
            if "interview" in content.lower():
                return AIMessage(content="""# Interview Preparation

## Potential Questions:
1. Tell me about yourself and your experience with AI in education.
2. How would you approach designing learning experiences for marginalized communities?
3. Describe a time when you had to adapt your teaching methods for different learning styles.

## Answers (STAR Method):
1. **Situation**: In my previous role, I worked on developing AI-powered educational tools.
**Task**: I needed to create accessible learning platforms for underserved communities.
**Action**: I collaborated with community leaders and educators to understand their specific needs.
**Result**: Successfully launched a program that increased engagement by 40%.

## Tips for Confidence:
- Practice your answers out loud
- Prepare specific examples from your experience
- Research the company's mission and values
- Prepare thoughtful questions to ask them""")
            
            elif "excel" in content.lower() or "pdf" in content.lower():
                return AIMessage(content="""# Reading Summary

**Title**: The Future of AI in Education

**Key Concepts & Definitions**:
• Artificial Intelligence in Education (AIEd) - The use of AI technologies to enhance learning experiences
• Personalized Learning - Tailoring educational content to individual student needs
• Learning Analytics - The measurement and analysis of learning data to improve outcomes

**Relevance & Curiosity**:
• Directly relevant to Livia's interests in leveraging AI for educational equity
• Connects to her work with marginalized communities and learning design
• Provides insights into career readiness and K-12 education applications""")
        
        return AIMessage(content="I'm a mock LLM for testing purposes. Please provide more specific instructions.")

def get_llm_config():
    """Get LLM configuration with fallback logic"""
    # First try Gemini
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            os.environ["GOOGLE_API_KEY"] = gemini_key
            return f"gemini/{gemini_model}"
        except Exception as e:
            print(f"Gemini failed: {e}")
    
    # If Gemini fails, try OpenAI
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_community.chat_models import ChatOpenAI
            return ChatOpenAI(model_name=openai_model, openai_api_key=openai_key)
        except Exception as e:
            print(f"OpenAI failed: {e}")
    
    # No API keys available
    print("No API keys available - LLM functionality disabled")
    return None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/interview', methods=['POST'])
def interview_preparation():
    """API endpoint for interview preparation"""
    try:
        data = request.get_json()
        cv_text = data.get('cv_text', '')
        job_description = data.get('job_description', '')
        
        if not cv_text or not job_description:
            return jsonify({'error': 'CV text and job description are required'}), 400
        
        # Configure LLM
        llm = get_llm_config()
        
        # Create agent and task
        interviewer = create_interviewer_agent(llm=llm)
        task = create_interview_task(interviewer, cv_text, job_description)
        
        # Create and run crew
        crew = Crew(
            agents=[interviewer],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        # Check if LLM is available
        if llm is None:
            return jsonify({
                'success': False,
                'error': 'LLM service not available. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable.'
            }), 500
        
        # Run crew with LLM
        result = crew.kickoff()
        
        return jsonify({
            'success': True,
            'result': str(result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def pdf_summarization():
    """API endpoint for PDF summarization"""
    try:
        # Check if file was uploaded
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No PDF file uploaded'}), 400
        
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        
        # Get custom interests if provided
        custom_interests = request.form.get('custom_interests', '').strip()
        
        # Configure LLM
        llm = get_llm_config()
        
        # Create agent and task with custom interests
        reader = create_reading_summary_agent(llm=llm, custom_interests=custom_interests)
        
        # Create temporary Excel path
        excel_filename = filename.replace('.pdf', '_summary.xlsx')
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
        
        # Combine default and custom interests for task
        interests_for_task = INTERESTS.copy()
        if custom_interests:
            # Split custom interests by comma and add to list
            custom_list = [i.strip() for i in custom_interests.split(',') if i.strip()]
            interests_for_task.extend(custom_list)
        
        task = create_reading_summary_task(reader, pdf_path, excel_path, interests_for_task)
        
        # Create and run crew
        crew = Crew(
            agents=[reader],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        # Check if LLM is available
        if llm is None:
            return jsonify({
                'success': False,
                'error': 'LLM service not available. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable.'
            }), 500
        
        # Run crew with LLM
        result = crew.kickoff()
        
        # Create Excel file from the agent's result
        excel_created = create_excel_from_summary(str(result), excel_path, filename)
        
        if excel_created and os.path.exists(excel_path):
            return jsonify({
                'success': True,
                'result': str(result),
                'excel_file': excel_filename
            })
        else:
            return jsonify({
                'success': True,
                'result': str(result),
                'excel_file': None,
                'message': 'Excel file could not be created from agent result'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cv')
def get_cv():
    """Get CV data from cv.json file"""
    try:
        cv_path = os.path.join(os.path.dirname(__file__), "resources", "cv.json")
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_data = json.load(f)
        return jsonify(cv_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Agent Assistant is running'})

# Initialize voice handlers globally
whisper_handler = None
tts_handler = None

def get_whisper_handler():
    """Get or initialize Whisper handler"""
    global whisper_handler
    if whisper_handler is None:
        try:
            whisper_handler = SpeechToTextHandler(model_size="base")
        except Exception as e:
            print(f"Warning: Could not initialize Whisper: {e}")
            return None
    return whisper_handler

def get_tts_handler():
    """Get or initialize TTS handler"""
    global tts_handler
    if tts_handler is None:
        try:
            tts_handler = TextToSpeechHandler()
        except Exception as e:
            print(f"Warning: Could not initialize TTS: {e}")
            return None
    return tts_handler

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio file to text using Whisper"""
    try:
        print("Transcription request received")
        
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            print("No audio file in request")
            return jsonify({'error': 'No audio file uploaded'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"Audio file received: {audio_file.filename}, size: {len(audio_file.read())}")
        audio_file.seek(0)  # Reset file pointer
        
        # Get Whisper handler
        whisper = get_whisper_handler()
        if not whisper:
            print("Whisper handler not available")
            return jsonify({'error': 'Speech-to-text service not available'}), 500
        
        # Save uploaded audio file temporarily
        filename = secure_filename(audio_file.filename or 'recording.wav')
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        print(f"Saving audio to: {temp_path}")
        
        audio_file.save(temp_path)
        
        # Check if file was saved
        if not os.path.exists(temp_path):
            print("Failed to save audio file")
            return jsonify({'error': 'Failed to save audio file'}), 500
        
        file_size = os.path.getsize(temp_path)
        print(f"Audio file saved, size: {file_size} bytes")
        
        if file_size == 0:
            print("Audio file is empty")
            os.unlink(temp_path)
            return jsonify({'error': 'Audio file is empty'}), 400
        
        try:
            # Transcribe audio
            print("Starting transcription...")
            transcribed_text = whisper.transcribe_audio_file(temp_path)
            print(f"Transcription completed: {len(transcribed_text)} characters")
            
            return jsonify({
                'success': True,
                'text': transcribed_text,
                'message': 'Audio transcribed successfully'
            })
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print("Temporary file cleaned up")
    
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice-status')
def voice_status():
    """Check if voice services are available"""
    try:
        whisper = get_whisper_handler()
        tts = get_tts_handler()
        
        return jsonify({
            'whisper_available': whisper is not None,
            'tts_available': tts is not None,
            'whisper_model': whisper.get_model_info() if whisper else None,
            'tts_voices': tts.get_voice_info() if tts else None
        })
    except Exception as e:
        return jsonify({
            'whisper_available': False,
            'tts_available': False,
            'error': str(e)
        })

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using OpenAI TTS"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text'].strip()
        voice = data.get('voice', 'nova')  # Default to female voice
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        tts_handler = get_tts_handler()
        if not tts_handler:
            return jsonify({'error': 'TTS service not available'}), 500
        
        # Convert text to speech
        audio_base64 = tts_handler.text_to_speech(text, voice)
        
        if audio_base64:
            return jsonify({
                'success': True,
                'audio_data': audio_base64,
                'voice_used': voice,
                'text_length': len(text)
            })
        else:
            return jsonify({'error': 'Failed to generate speech'}), 500
            
    except Exception as e:
        print(f"Error in TTS endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
