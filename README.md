# AI Agents Class
MIT MAS.665 class work on AI Agents and the Agentic Web.

## Overview
This project provides AI agents to help with:
1. **Job Interview Preparation** - Generate interview questions and answers based on CV and job description
2. **PDF Reading Summarization** - Summarize academic readings and create Excel files with key concepts

## Features
- 🤖 **Interview Helper Agent** - Prepares interview questions and answers in your voice
- 📚 **Reading Summarizer Agent** - Summarizes PDF readings with focus on your interests
- 🔧 **Multi-LLM Support** - Works with both OpenAI and Google Gemini models
- 📊 **Excel Output** - Automatically creates structured Excel files from summaries
- 📄 **PDF Processing** - Converts PDFs to text for analysis

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

### 4. Prepare Your Files
- **CV File**: Place your CV data in `cv.json` (JSON format)
- **PDF File**: Place any PDF reading in `example_reading.pdf` (optional)

### 5. Run the Application
```bash
python main.py
```

## Usage

### Interview Preparation
1. Run the application
2. Enter your job description (or use the default)
3. The Interview Helper agent will generate:
   - Potential interview questions
   - Answers in your voice using STAR method
   - Tips for confidence and preparation

### PDF Summarization
1. Run the application
2. Choose "y" when asked about PDF summarization
3. Provide the PDF file path (default: `example_reading.pdf`)
4. Specify Excel output path (default: `reading_summary.xlsx`)
5. The Reading Summarizer agent will:
   - Read and analyze the PDF content
   - Extract key concepts relevant to your interests
   - Create an Excel file with structured summary

## Configuration

### LLM Selection
- **OpenAI**: Set `LLM_TYPE=openai` in `.env`
- **Gemini**: Set `LLM_TYPE=gemini` in `.env`

### Interests (for PDF summarization)
The system focuses on these topics when summarizing readings:
- Leveraging AI in education
- Marginalized communities
- EdTech
- Learning design
- Career readiness
- K-12 education
- Soft skill development

## File Structure
```
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── cv.json                # Your CV data (JSON format)
├── example_reading.pdf    # Sample PDF for testing
├── reading_summary.xlsx   # Generated Excel output
└── .env                   # API keys and configuration
```

## Dependencies
- `crewai` - AI agent framework
- `langchain-google-genai` - Gemini LLM integration
- `pypdf` - PDF text extraction
- `pandas` - Data manipulation
- `openpyxl` - Excel file creation
- `python-dotenv` - Environment variables

## Troubleshooting

### Python Version Issues
If you get Python version errors, make sure you're using Python 3.12:
```bash
python3.12 --version
```

### API Key Issues
- Check your `.env` file has the correct API keys
- Verify your API keys are valid and have sufficient quota
- For Gemini, ensure `GOOGLE_API_KEY` is set in your environment

### PDF Reading Issues
- Ensure the PDF file exists and is readable
- The system will create a temporary text file for processing
- Check file permissions in your directory

## Example Output
- **Interview Preparation**: Structured Q&A with STAR method answers
- **PDF Summary**: Excel file with columns for Name, Key Concepts & Definitions, and Relevance & Curiosity