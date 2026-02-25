# Agent Demo

A demo to two LangGraph agents for learning purposes.

## Requirements

- Python 3.11+
- Local LLM model or API Key

## Setup

```bash
git clone https://github.com/DGupt4/agent-demo.git
cd agent-demo
python -m venv .venv
source .venv/bin/activate        
pip install -r requirements.txt
```

## LLM

Open `graph.py` in either agent folder and update these two lines:

```python
model="your-model-name-here"
api_key="your-api-key-here"
```

## Running

```bash
# Calculator agent
cd calculator_agent
python main.py

# Debate agent
cd debate_agent
python main.py "<DEBATE TOPIC>"
```