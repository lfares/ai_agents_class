# Web Platform Setup Guide

## Overview
This guide will help you set up and run the AI Agent Assistant web platform locally.

## Prerequisites
- Python 3.12
- Virtual environment (venv312)
- API keys (OpenAI or Gemini)

## Quick Start

### 1. Install Web Dependencies
```bash
# Activate your virtual environment
source venv312/bin/activate

# Install additional web dependencies
pip install flask werkzeug
```

### 2. Start the Web Server
```bash
# Run the Flask application
python app.py
```

### 3. Access the Platform
Open your browser and go to: `http://localhost:5000`

## Features

### 🎨 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Beautiful UI**: Modern gradient design with smooth animations
- **Interactive Elements**: Drag & drop file uploads, real-time feedback

### 🤖 Two AI Agents
1. **Interview Helper**: Generate interview questions and answers
2. **Reading Summarizer**: Summarize PDFs and create Excel reports

### 📱 User Experience
- **File Upload**: Drag & drop or click to upload PDFs and JSON files
- **Real-time Processing**: Live loading indicators and progress feedback
- **Download Results**: Direct download links for generated Excel files
- **Error Handling**: Clear error messages and notifications

## Usage

### Interview Preparation
1. Click "Start Interview Prep"
2. Paste your CV information or upload a JSON file
3. Enter the job description
4. Click "Generate Interview Prep"
5. View your personalized interview questions and answers

### PDF Summarization
1. Click "Upload PDF"
2. Drag & drop or select a PDF file
3. Click "Summarize PDF"
4. View the summary and download the Excel file

## File Structure
```
├── app.py                 # Flask web application
├── main.py               # Original agent functions
├── templates/
│   └── index.html        # Main web page
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling
│   └── js/
│       └── app.js        # Interactive functionality
├── uploads/              # Temporary file storage
└── requirements.txt      # All dependencies
```

## API Endpoints

### Interview Preparation
- **POST** `/api/interview`
- **Body**: `{"cv_text": "...", "job_description": "..."}`
- **Response**: Interview preparation text

### PDF Summarization
- **POST** `/api/summarize`
- **Body**: Form data with PDF file
- **Response**: Summary text and Excel file download link

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
# If port 5000 is busy, change it in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### 2. File Upload Errors
- Check file size (max 16MB)
- Ensure file format is PDF or JSON
- Verify upload directory permissions

#### 3. API Key Issues
- Verify your `.env` file has correct API keys
- Check API key quotas and billing
- Ensure environment variables are loaded

#### 4. Agent Errors
- Check that all dependencies are installed
- Verify your CV.json file exists
- Ensure PDF files are readable

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
