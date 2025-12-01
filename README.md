# YouTube AI Content Detector

🎯 **Detect AI-generated content and dangerous material from YouTube videos**

A full-stack web application that analyzes YouTube videos using cutting-edge AI to identify:
- 🤖 **AI-Generated Content**: Detect if content was created by AI (ChatGPT scripts, AI voice synthesis, etc.)
- ⚠️ **Dangerous Content**: Flag harmful, illegal, or policy-violating material

## 🏗️ Architecture

```
┌─────────────┐
│ React       │  User Interface (Vite + Modern UI)
│ Frontend    │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│ FastAPI     │  REST API Server
│ Server      │
└──────┬──────┘
       │
┌──────▼──────┐
│ Redis       │  Message Queue
│ Queue       │
└──────┬──────┘
       │
┌──────▼──────┐
│ Celery      │  Async Worker
│ Worker      │
└──────┬──────┘
       │
   ┌───┴─────────────┬───────────────┬──────────────┐
   │                 │               │              │
┌──▼──────┐  ┌──────▼─────┐  ┌─────▼────┐  ┌─────▼─────┐
│ yt-dlp  │  │  FFmpeg    │  │ Whisper  │  │ Gemini/   │
│Download │  │Media Proc  │  │Transcribe│  │ GPT LLM   │
└─────────┘  └────────────┘  └──────────┘  └───────────┘
```

## ✨ Features

- **YouTube Integration**: Download and process any public YouTube video
- **Speech-to-Text**: Accurate transcription using OpenAI's Whisper AI
- **AI Content Detection**: Advanced LLM analysis (Gemini or GPT-4) to identify AI-generated content
- **Safety Analysis**: Detect dangerous content including violence, hate speech, misinformation, scams, etc.
- **Real-time Updates**: Async processing with live status updates
- **Modern UI**: Beautiful dark-themed interface with glassmorphism and smooth animations
- **Containerized**: Full Docker setup for easy deployment

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- API Keys:
  - OpenAI API Key (for Whisper and/or GPT)
  - Google Gemini API Key (optional, alternative to GPT)

### Installation

1. **Clone the repository**
   ```bash
   cd ETRICA/youtube-ai-detector
   ```

2. **Configure Environment Variables**
   
   Edit the `.env` file in the root directory:
   ```env
   # API Keys - REPLACE WITH YOUR ACTUAL KEYS
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # LLM Provider (options: openai, gemini)
   LLM_PROVIDER=gemini
   
   # Whisper Model Size (options: tiny, base, small, medium, large)
   WHISPER_MODEL_SIZE=base
   ```

3. **Start the Application**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage

1. **Submit a Video**
   - Open http://localhost:3000
   - Paste a YouTube URL
   - Click "Analyze Video"

2. **Wait for Analysis**
   - The system will:
     - Download the video/audio
     - Transcribe speech to text
     - Analyze content with AI
   - Typically takes 2-5 minutes depending on video length

3. **View Results**
   - AI Generation Score (0-100%)
   - Dangerous Content Flags
   - Full Transcription
   - Detailed Analysis

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Celery**: Distributed task queue
- **Redis**: Message broker
- **PostgreSQL**: Database
- **yt-dlp**: YouTube downloader
- **FFmpeg**: Media processing
- **Whisper AI**: Speech transcription
- **Google Gemini / OpenAI GPT**: Content analysis

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool
- **Axios**: HTTP client
- **Custom CSS**: Premium dark theme

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Frontend web server

## 📁 Project Structure

```
youtube-ai-detector/
├── client/                     # React Frontend
│   ├── src/
│   │   ├── components/        # UI Components
│   │   │   ├── AnalyzeForm.jsx
│   │   │   └── ResultsDisplay.jsx
│   │   ├── App.jsx
│   │   ├── index.css          # Design System
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── server/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py   # REST API Routes
│   │   ├── core/
│   │   │   └── config.py      # Configuration
│   │   ├── models/
│   │   │   ├── database.py    # DB Connection
│   │   │   └── models.py      # ORM Models
│   │   ├── services/          # Core Services
│   │   │   ├── downloader.py  # YouTube Downloader
│   │   │   ├── media_proc.py  # FFmpeg Processing
│   │   │   ├── transcriber.py # Whisper AI
│   │   │   └── llm_analyzer.py # LLM Analysis
│   │   ├── worker/
│   │   │   └── tasks.py       # Celery Tasks
│   │   ├── celery_app.py      # Celery Config
│   │   └── main.py            # FastAPI App
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/                       # Persistent Data
│   ├── postgres/              # Database Files
│   └── redis/                 # Redis Data
│
├── .env                        # Environment Variables
├── .gitignore
├── docker-compose.yml          # Docker Orchestration
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for Whisper/GPT | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required if using Gemini |
| `LLM_PROVIDER` | LLM to use (`openai` or `gemini`) | `gemini` |
| `WHISPER_MODEL_SIZE` | Whisper model (`tiny`, `base`, `small`, `medium`, `large`) | `base` |
| `DATABASE_URL` | PostgreSQL connection URL | Auto-configured |
| `REDIS_URL` | Redis connection URL | Auto-configured |

### Whisper Model Sizes

| Model | Speed | Accuracy | Memory |
|-------|-------|----------|--------|
| tiny | Fastest | Low | ~1 GB |
| base | Fast | Good | ~1 GB |
| small | Medium | Better | ~2 GB |
| medium | Slow | Great | ~5 GB |
| large | Slowest | Best | ~10 GB |

## 📡 API Endpoints

### `POST /api/analyze`
Submit a YouTube URL for analysis

**Request:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "job_id": 123,
  "status": "pending",
  "message": "Analysis job submitted successfully"
}
```

### `GET /api/status/{job_id}`
Check job status

**Response:**
```json
{
  "job_id": 123,
  "status": "processing",
  "youtube_url": "...",
  "created_at": "2024-01-01T00:00:00"
}
```

### `GET /api/result/{job_id}`
Get completed analysis results

**Response:**
```json
{
  "job_id": 123,
  "status": "completed",
  "result": {
    "video_info": { ... },
    "transcription": { ... },
    "analysis": {
      "ai_generated_score": 75,
      "dangerous_content": false,
      ...
    }
  }
}
```

### `GET /api/jobs`
List recent analysis jobs

## 🧪 Development

### Running Without Docker

**Backend:**
```bash
cd server
pip install -r requirements.txt
uvicorn app.main:app --reload

# In another terminal
celery -A app.celery_app worker --loglevel=info
```

**Frontend:**
```bash
cd client
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests (when implemented)
cd server
pytest

# Frontend tests (when implemented)
cd client
npm test
```

## 🐛 Troubleshooting

### Whisper Model Download Issues
- First run downloads the model (~100MB-3GB depending on size)
- Can take 5-10 minutes on slow connections
- Models are cached in `data/models/`

### Out of Memory
- Try a smaller Whisper model (`tiny` or `base`)
- Increase Docker memory limits
- Process shorter videos

### API Rate Limits
- OpenAI/Gemini have rate limits
- Consider adding retry logic or rate limiting

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [FFmpeg](https://ffmpeg.org/) - Media processing
