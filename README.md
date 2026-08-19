# Vaani 🎙

Vaani is a high-performance voice assistant supporting **Hindi, Gujarati, and English**. It combines local GPU-accelerated speech processing with fast online AI via the **Groq Cloud API**.

1. Filters out background noise and static from microphone input.
2. Transcribes speech to text using `faster-whisper` (medium model).
3. Detects input language and translates non-English speech (Hindi/Gujarati) to English using Meta's `NLLB-200`.
4. Communicates with Groq Cloud API using a warm, natural **Human Persona**.
5. Translates English responses back to the user's input language.
6. Synthesizes and speaks responses using Edge-TTS neural voice synthesis.

---

## Key Features
- **GPU-Accelerated Processing:** Supports NVIDIA CUDA GPU execution for STT (`faster-whisper`) and Neural Machine Translation (`NLLB-200`).
- **Human Conversational Persona:** Communicates naturally like a real human friend—no robotic disclaimers or artificial AI jargon.
- **Groq Cloud API Integration:** Lightning-fast online LLM responses using `groq/compound`.
- **Multilingual Support:** Seamlessly converses back in Hindi, Gujarati, or English.
- **Modern Glassmorphic UI:** Reactive React + Vite frontend dashboard alongside a robust FastAPI backend.

---

## Project Structure

```
Vaani/
├── app/                      # FastAPI Backend Application
│   ├── core/                 # AI Engines & Audio Modules
│   │   ├── audio_capture.py  # Mic capture & WebRTC VAD
│   │   ├── audio_denoiser.py # Dynamic noise reduction
│   │   ├── response_generator.py # Groq Cloud API & Human Persona
│   │   ├── stt_engine.py     # Faster-Whisper Speech-to-Text
│   │   ├── translation_engine.py # NLLB-200 Neural Translator
│   │   └── voice_synthesizer.py  # Edge-TTS / SAPI5 Speech Synthesis
│   ├── middleware/           # CORS & Rate Limiting Middleware
│   ├── services/             # Pipeline Orchestration Service
│   ├── api.py                # FastAPI REST API Endpoints
│   └── config.py             # Global Environment Settings
├── tests/                    # Comprehensive Test Suite
├── vaani-ui/                 # React + Vite Frontend App
│   ├── src/
│   │   ├── components/       # Glassmorphic UI Components
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── .env                      # Environment Variables (GROQ_API_KEY)
├── .env.example              # Environment Template
├── requirements.txt          # Backend Dependencies
└── vaani_api.py              # Server Entrypoint
```

---

## Getting Started

### Prerequisites
- **Python:** 3.10 to 3.13
- **Node.js:** 18 or higher
- **Groq API Key:** Obtain an API key from [Groq Console](https://console.groq.com/).

---

### Setup & Execution

#### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate      # Windows PowerShell

# Install backend dependencies
pip install -r requirements.txt

# Download offline models (Whisper Medium & NLLB-200)
python download_models.py
```

#### 2. Environment Configuration
Create a `.env` file at the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=groq/compound
VAANI_WHISPER_MODEL=medium
```

#### 3. Launch Services

**Terminal 1 (Backend Server):**
```bash
python vaani_api.py
```
*Backend runs on `http://localhost:8001`*

**Terminal 2 (Frontend Dashboard):**
```bash
cd vaani-ui
npm install
npm run dev
```
*Frontend UI runs on `http://localhost:5173`*
