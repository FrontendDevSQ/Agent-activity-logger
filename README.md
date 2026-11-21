# Agent Activity Logger

An observability and security guard project for tool-calling AI agents. It records every step of an agent's execution in SQLite with a SHA-256 hash chain, checks untrusted tool outputs and tool arguments for prompt injection or risky behavior, and provides a web viewer to inspect sessions and verify log integrity.

## Why This Exists

Autonomous or tool-calling agents can read untrusted content from files or external sources. If hidden instructions are embedded inside that data, an agent may trigger unintended or risky tool calls without clear visibility. This project gives you:

- **Step-by-step audit trails** of user tasks, model decisions, tool calls with explicit `reason` fields, tool outputs, and final responses.
- **Pre- and post-tool security checks** (`detect.py`) to spot prompt injection patterns, sensitive file access, path traversal, or risky commands.
- **Tamper-evident logging** (`logger.py` & `tamper.py`) using a SHA-256 hash chain (`prev_hash` -> `hash`) and integrity verification.
- **Interactive log viewer** (`viewer.py` + `templates/index.html`) to browse sessions, inspect events, and test tamper detection.

## Project Structure

```text
agent-logger/
├── agent.py            # Sandbox tools and scenario setup (normal / attack)
├── real_agent.py       # LLM agent loop with tool calling (Groq, Gemini, OpenAI)
├── detect.py           # Prompt injection & risky tool-call checks
├── logger.py           # SQLite storage, redaction, and SHA-256 hash chain
├── tamper.py           # Demo script that modifies a high-risk log row
├── viewer.py           # Flask web UI & API for viewing logs and verifying chain
├── requirements.txt    # Python dependencies
├── sandbox/            # Sample files used during runs
└── templates/
    └── index.html      # Web dashboard template
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key** (for `real_agent.py`)

   PowerShell:
   ```powershell
   $env:PROVIDER="groq"
   $env:GROQ_API_KEY="your_api_key_here"
   ```

   Optional provider/model overrides:
   - `PROVIDER`: `groq` (default), `gemini`, or `openai`
   - `MODEL`: override the default model for the selected provider

## Usage

### 1. Run the agent in `normal` or `attack` mode

```bash
python real_agent.py normal
python real_agent.py attack
```

### 2. Open the log viewer

```bash
python viewer.py
```

Open `http://127.0.0.1:5000` in your browser to inspect sessions, events, and alerts.

### 3. Test tamper detection

1. Run an `attack` session so a high-risk event is recorded.
2. Run the tamper demo script:

   ```bash
   python tamper.py
   ```

3. Click **Verify log integrity** in the web viewer to confirm that modification is detected.




