# Smart Code Review Agent 🔍

An AI-powered Python code review agent built with Google's **Agent Development Kit (ADK)** and **Gemini**, deployed as a serverless service on **Google Cloud Run**.

The agent analyzes Python code across four dimensions — **bugs**, **style**, **security**, and **overall quality** — and returns structured, actionable feedback through a simple REST API.

---

## Features

- **Multi-dimensional review**: Analyzes code for bugs, style violations, security vulnerabilities, and computes a quality score
- **Intelligent tool selection**: The agent decides which review tools to invoke based on the code content — a security review only runs when the code involves file I/O, database queries, or user input handling
- **Dual input support**: Submit code as raw text or provide a GitHub raw URL / Gist link
- **Structured output**: Returns organized findings with severity levels, line references, and actionable suggestions
- **Production-grade**: Input validation, error handling, health checks, and proper HTTP status codes
- **Serverless deployment**: Runs on Cloud Run with automatic scaling and HTTPS

---

## Architecture

```
HTTP POST Request
       │
       ▼
┌─────────────────┐
│   FastAPI App    │  ← Input validation, URL fetching
│   (app.py)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ADK Runner     │  ← Session management, event streaming
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LlmAgent       │  ← Gemini 2.5 Flash
│   (agent.py)     │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬──────────────┐
    ▼          ▼          ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│analyze │ │check   │ │review    │ │calculate │
│_bugs   │ │_style  │ │_security │ │_score    │
└────────┘ └────────┘ └──────────┘ └──────────┘
                                   (runs last)
```

The agent uses **four custom FunctionTools**. The LLM autonomously decides which tools to call:
- `analyze_bugs` and `check_style` run on every review
- `review_security` only runs when security-relevant patterns are detected
- `calculate_score` always runs last, using findings from other tools to compute the final score

---

## Project Structure

```
smart-code-review-agent/
├── code_review_agent/          # ADK agent package
│   ├── __init__.py             # Exports root_agent
│   ├── agent.py                # LlmAgent definition
│   ├── tools.py                # Four FunctionTool implementations
│   ├── prompt.py               # System instructions
│   └── .env                    # API key (not committed)
├── app.py                      # FastAPI HTTP wrapper
├── Dockerfile                  # Container config for Cloud Run
├── .dockerignore               # Files excluded from container
├── .gitignore                  # Files excluded from Git
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## API Reference

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "code_review_agent"
}
```

### `POST /review`

Submit Python code for review.

**Request body** (provide one of `code` or `url`):
```json
{
  "code": "def add(a, b):\n    return a + b"
}
```
or
```json
{
  "url": "https://raw.githubusercontent.com/user/repo/main/script.py"
}
```

**Success response:**
```json
{
  "status": "success",
  "review": "## Code Review Results\n\n..."
}
```

**Error response:**
```json
{
  "status": "error",
  "error": "Description of what went wrong"
}
```

### `GET /docs`

Interactive Swagger UI for testing the API in your browser.

---

## Quick Start

### Prerequisites
- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/app/apikey)

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/smart-code-review-agent.git
cd smart-code-review-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "GOOGLE_API_KEY=your_key_here" > code_review_agent/.env

# Test with ADK Dev UI
adk web

# Or run the HTTP server
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### Test with curl

```bash
# Health check
curl http://localhost:8080/health

# Review raw code
curl -X POST http://localhost:8080/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b):\n    return a + b"}'

# Review from GitHub URL
curl -X POST http://localhost:8080/review \
  -H "Content-Type: application/json" \
  -d '{"url": "https://raw.githubusercontent.com/user/repo/main/script.py"}'
```

---

## Deployment (Cloud Run)

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config set run/region asia-south1

# Deploy
gcloud run deploy code-review-agent \
  --source . \
  --set-env-vars="GOOGLE_API_KEY=your_key_here" \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=120
```

---

## Skills Demonstrated

| Skill | Implementation |
|-------|---------------|
| ADK project structure | Standard folder layout, `__init__.py` exports `root_agent` |
| Tool-using agent | Four custom `FunctionTool`s with descriptive docstrings |
| LLM decision-making | Agent selectively invokes tools based on code content |
| Structured output | Consistent JSON responses with severity levels and scores |
| Cloud Run deployment | Dockerized, serverless, publicly accessible HTTP endpoint |
| Production quality | Input validation, error handling, health checks, proper HTTP status codes |

---

## Tech Stack

- **Agent Framework**: Google Agent Development Kit (ADK)
- **LLM**: Gemini 2.5 Flash
- **HTTP Framework**: FastAPI + Uvicorn
- **Deployment**: Google Cloud Run (serverless)
- **Language**: Python 3.11

---

## License

This project was built as part of the Google ADK learning track.
