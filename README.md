# Digital Self AI

A persistent, local-first AI that replicates the user's personality, remembers specific details explicitly, and interacts via Voice and Text using a ChatGPT-like interface.

## Tech Stack
- **Frontend**: Next.js (React), Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Explicit Memory & Identity)
- **AI Core**: Ollama (LLM)
- **Voice**: Web Speech API (Browser) + VOSK (Headless)

## Prerequisites
1.  **Python 3.10+**
2.  **Node.js 18+**
3.  **PostgreSQL**: Running locally or accessible.
4.  **Ollama**: Running with `llama3` pulled (`ollama pull llama3`).

## Setup

### 1. Backend
```powershell
# Navigate to project root
pip install -r requirements.txt
python backend/api_server.py
```
*The server runs on http://localhost:8000. It will auto-initialize the Database schema on first run.*

### 2. Frontend
```powershell
cd web_ui
npm install
npm run dev
```
*The UI runs on http://localhost:3000.*

## Features
- **ChatGPT UI**: Dark mode, sidebar, message history.
- **Explicit Memory**: Type "Remember I like X" to store long-term memories.
- **Memory View**: Click "Dataset" in the sidebar to see what the bot knows.
- **Voice Mode**: Click the headphone icon to speak; the bot listens and speaks back (TTS).
- **Attachments**: Attach text files for context.

## Configuration
- **Database**: configured in `brain/db.py` (Default: `localhost:5432`, user `postgres`, db `antigravity`).
- **Identity**: configured in `brain/db.py` (Default: "Human-like" personality).
