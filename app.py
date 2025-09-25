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

def get_llm_config():
    """Get LLM configuration from environment"""
    llm_type = os.environ.get("LLM_TYPE", "openai").lower()
    
    if llm_type == "gemini":
        gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key
            return f"gemini/{gemini_model}"
    
    # Default to OpenAI
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        from langchain_community.chat_models import ChatOpenAI
        return ChatOpenAI(model_name=openai_model, openai_api_key=openai_key)
    
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
        
        # Configure LLM
        llm = get_llm_config()
        
        # Create agent and task
        reader = create_reading_summary_agent(llm=llm)
        
        # Create temporary Excel path
        excel_filename = filename.replace('.pdf', '_summary.xlsx')
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
        
        task = create_reading_summary_task(reader, pdf_path, excel_path, INTERESTS)
        
        # Create and run crew
        crew = Crew(
            agents=[reader],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Create Excel file from summary
        pdf_name = filename.replace('.pdf', '')
        success = create_excel_from_summary(str(result), excel_path, pdf_name)
        
        if success and os.path.exists(excel_path):
            return jsonify({
                'success': True,
                'result': str(result),
                'excel_file': excel_filename
            })
        else:
            return jsonify({
                'success': True,
                'result': str(result),
                'excel_file': None
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
        cv_path = os.path.join(os.path.dirname(__file__), "cv.json")
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_data = json.load(f)
        return jsonify(cv_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Agent Assistant is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
