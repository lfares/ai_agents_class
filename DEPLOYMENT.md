# Deployment Guide

## Quick Deploy to Railway (Recommended)

1. **Sign up for Railway**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Connect your repository**: 
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
3. **Set environment variables** (optional):
   - `GEMINI_API_KEY`: Your Gemini API key (if you have one)
   - `OPENAI_API_KEY`: Your OpenAI API key (if you have one)
   - `LLM_TYPE`: Set to "gemini" or "openai" (defaults to demo mode)
4. **Deploy**: Railway will automatically deploy your app!

## Alternative: Deploy to Render

1. **Sign up for Render**: Go to [render.com](https://render.com) and sign up
2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Choose "Web Service"
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. **Set environment variables** (optional):
   - `GEMINI_API_KEY`: Your Gemini API key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LLM_TYPE`: Set to "gemini" or "openai"
4. **Deploy**: Render will build and deploy your app!

## Environment Variables

- `GEMINI_API_KEY`: For Gemini AI (optional - falls back to demo mode)
- `OPENAI_API_KEY`: For OpenAI (optional - falls back to demo mode)
- `LLM_TYPE`: "gemini", "openai", or "default" (defaults to demo mode)
- `PORT`: Automatically set by the hosting platform

## Demo Mode

If no API keys are provided, the app runs in demo mode with:
- Sample interview preparation
- Sample PDF summarization with Excel output
- All features work without external API calls

## File Structure

```
├── app.py                 # Main Flask application
├── main.py               # Core AI agent logic
├── requirements.txt      # Python dependencies
├── Procfile             # Deployment configuration
├── runtime.txt          # Python version
├── templates/           # HTML templates
├── static/             # CSS and JavaScript
└── uploads/            # File uploads directory
```

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Visit http://localhost:5002
```

## Notes

- The app automatically falls back to demo mode if API keys are not available
- File uploads are stored in the `uploads/` directory
- The app works with or without external AI services
- All features are fully functional in demo mode
