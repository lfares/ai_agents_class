# AI Agents Class
MIT MAS.665 class work on AI Agents and the Agentic Web.

## Local setup

1) Create a local `.env` file with your OpenAI credentials (recommended)

```bash
# create a .env file and add your OpenAI key and preferred model
cat > .env <<'EOF'
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
EOF
```

2) Create and activate a virtual environment (Python 3.12)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

3) Install requirements

```bash
pip install -r requirements.txt
```

4) Run the hw1 app

```bash
python main.py
```