# AI Agents Class
MIT MAS.665 class work on AI Agents and the Agentic Web.

## Local setup

1) Create a local `.env` file

```bash
echo "GEMINI_API_KEY=YOUR_API_KEY_HERE" >> .env
echo "MODEL_NAME=gemini/gemini-1.5-pro-latest" >> .env
```

2) Create and activate a virtual environment (Python 3.12)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

3) Go to the `hw1` folder and install requirements

```bash
cd hw1
pip install -r requirements.txt
```

4) Run the hw1 app

```bash
python main.py
```