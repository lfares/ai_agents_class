# Deployment Guide

## Environment Variables Setup

For deployment, you need to set these environment variables on your hosting platform:

### Required Environment Variables

```bash
# LLM Configuration
LLM_TYPE=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Flask Configuration
FLASK_ENV=production
PORT=5000
```

### Platform-Specific Instructions

#### Heroku
1. Go to your Heroku app dashboard
2. Navigate to Settings → Config Vars
3. Add each environment variable:
   - `LLM_TYPE` = `gemini`
   - `GEMINI_API_KEY` = `your_actual_api_key`
   - `GEMINI_MODEL` = `gemini-2.0-flash`
   - `FLASK_ENV` = `production`
   - `PORT` = `5000`

#### Railway
1. Go to your Railway project dashboard
2. Navigate to Variables tab
3. Add each environment variable as above

#### Render
1. Go to your Render service dashboard
2. Navigate to Environment tab
3. Add each environment variable as above

#### Vercel
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add each environment variable as above

## Local Development

1. Copy `.env.example` to `.env`
2. Add your actual API keys to `.env`
3. Run: `python app.py`

## Security Notes

- Never commit `.env` files to git
- Use different API keys for development and production
- Monitor your API usage and costs
- Consider using environment-specific API keys