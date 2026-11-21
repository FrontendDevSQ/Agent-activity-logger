# Agent Activity Logger (Agentic AI Security)

Records every decision and tool call an AI agent makes, with a reason, and shows them on a timeline.
It also detects prompt injection and sensitive or dangerous actions.

## Setup
    pip install -r requirements.txt
    export GROQ_API_KEY=your_key      # Windows PowerShell: $env:GROQ_API_KEY="your_key"

## Run
    python real_agent.py normal       # real LLM, clean task
    python real_agent.py attack       # real LLM, task file contains a prompt injection
    python agent.py attack            # offline mock agent (no API key needed)
    GUARD=block python real_agent.py attack   # guard blocks risky calls (default: monitor)
    python viewer.py                  # open http://127.0.0.1:5000

## Files
- logger.py: SQLite log with a hash chain (tamper-evident) and integrity check
- detect.py: prompt-injection, sensitive-access, path-traversal and dangerous-command detection
- agent.py: sandboxed tools, guard (monitor/block) and mock agent
- real_agent.py: LLM agent using Groq, Gemini or OpenAI-compatible APIs
- viewer.py + templates/index.html: timeline viewer
