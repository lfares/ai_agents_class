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
            print(f"Gemini failed: {e}, falling back to demo mode")
    
    # If Gemini fails, try OpenAI
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_community.chat_models import ChatOpenAI
            return ChatOpenAI(model_name=openai_model, openai_api_key=openai_key)
        except Exception as e:
            print(f"OpenAI failed: {e}, falling back to demo mode")
    
    # Fallback to demo mode
    print("Using demo mode - no API keys available")
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
        
        # Check if we're in demo mode
        if llm is None:
            # Demo mode - return comprehensive interview preparation
            demo_result = """# Interview Preparation

## Potential Questions & Answers:

### 1. Tell me about yourself and your experience with AI in education.
**Answer (STAR Method):**
- **Situation**: I'm a graduate student at MIT focusing on AI applications in education, with particular interest in serving marginalized communities.
- **Task**: I've been working on developing AI-powered educational tools that can adapt to different learning styles and cultural contexts.
- **Action**: I've collaborated with educators, community leaders, and students to understand their specific needs and co-design solutions.
- **Result**: This work has led to increased engagement rates and more personalized learning experiences for underserved populations.

### 2. How would you approach designing learning experiences for marginalized communities?
**Answer (STAR Method):**
- **Situation**: During my research, I identified significant gaps in educational technology accessibility for marginalized communities.
- **Task**: I needed to create inclusive learning platforms that respect cultural differences and address specific barriers.
- **Action**: I conducted extensive community outreach, partnered with local organizations, and implemented user-centered design principles.
- **Result**: Developed a framework that increased participation by 60% and received positive feedback from community stakeholders.

### 3. Describe a time when you had to adapt your teaching methods for different learning styles.
**Answer (STAR Method):**
- **Situation**: I was teaching a diverse group of students with varying technical backgrounds and learning preferences.
- **Task**: I needed to ensure all students could effectively engage with complex AI concepts regardless of their starting point.
- **Action**: I implemented multiple teaching modalities including visual diagrams, hands-on coding exercises, and collaborative discussions.
- **Result**: Student satisfaction increased by 45% and all students successfully completed the course with improved understanding.

### 4. How do you stay current with developments in AI and educational technology?
**Answer:**
- I actively participate in academic conferences like AERA and AIED
- I follow key researchers and practitioners on social media and academic networks
- I engage in hands-on experimentation with new tools and platforms
- I maintain connections with industry professionals and educators
- I contribute to open-source educational technology projects

### 5. What challenges do you see in implementing AI in K-12 education?
**Answer:**
- **Equity and Access**: Ensuring AI tools don't widen the digital divide
- **Teacher Training**: Supporting educators in effectively integrating AI tools
- **Data Privacy**: Protecting student information while enabling personalized learning
- **Curriculum Integration**: Aligning AI tools with existing educational standards
- **Cultural Sensitivity**: Ensuring AI respects diverse cultural contexts and values

### 6. How would you measure the success of an AI-powered educational intervention?
**Answer:**
- **Learning Outcomes**: Standardized test scores, project completion rates, and skill assessments
- **Engagement Metrics**: Time spent on platform, interaction rates, and student feedback
- **Equity Indicators**: Participation rates across different demographic groups
- **Long-term Impact**: Career readiness, continued learning, and real-world application
- **Qualitative Feedback**: Teacher and student testimonials, case studies, and observations

## Tips for Confidence:
- Practice your answers out loud, focusing on the STAR method structure
- Prepare specific examples from your experience with concrete numbers and outcomes
- Research the company's mission, values, and recent projects
- Prepare thoughtful questions about their AI initiatives and educational impact
- Be ready to discuss how your research interests align with their goals
- Practice explaining complex AI concepts in simple, accessible terms"""
            
            return jsonify({
                'success': True,
                'result': demo_result,
                'demo_mode': True
            })
        else:
            # Normal mode - run crew
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
        
        # Check if we're in demo mode
        if llm is None:
            # Demo mode - create Excel file directly and return structured data
            try:
                import pandas as pd
                data = {
                    'Name': ['The Future of AI in Education'],
                    'Key concepts & Definitions': ['• Artificial Intelligence in Education (AIEd) - The use of AI technologies to enhance learning experiences\n• Personalized Learning - Tailoring educational content to individual student needs\n• Learning Analytics - The measurement and analysis of learning data to improve outcomes'],
                    'Relevance & Curiosity': ['• Directly relevant to Livia\'s interests in leveraging AI for educational equity\n• Connects to her work with marginalized communities and learning design\n• Provides insights into career readiness and K-12 education applications']
                }
                df = pd.DataFrame(data)
                df.to_excel(excel_path, index=False)
                
                # Return structured data for the platform to display
                return jsonify({
                    'success': True,
                    'result': 'Demo mode: Excel file created with sample data',
                    'excel_file': excel_filename,
                    'demo_mode': True,
                    'structured_data': {
                        'title': 'The Future of AI in Education',
                        'key_concepts': [
                            'Artificial Intelligence in Education (AIEd) - The use of AI technologies to enhance learning experiences',
                            'Personalized Learning - Tailoring educational content to individual student needs',
                            'Learning Analytics - The measurement and analysis of learning data to improve outcomes'
                        ],
                        'relevance': [
                            'Directly relevant to Livia\'s interests in leveraging AI for educational equity',
                            'Connects to her work with marginalized communities and learning design',
                            'Provides insights into career readiness and K-12 education applications'
                        ]
                    }
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Demo mode error: {str(e)}'
                })
        else:
            # Normal mode - run crew
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
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
