# SAGE7 Setup Instructions

## 🚨 IMPORTANT SECURITY NOTICE

The `.env.local` file previously contained exposed API keys. These have been replaced with placeholders for security. **You must replace these with your own valid API keys.**

## 📋 Prerequisites

- **Python 3.8+** for backend (FastAPI, Uvicorn)
- **Node.js 18+** for frontend (Vite, React)
- **Valid API Keys** for the services below

## 🔑 Required API Keys

### 1. OpenRouter API Key
- Get from: https://openrouter.ai/keys
- Required for: AI chat, coding analysis (multi-model access)
- Set as: `OPENROUTER_API_KEY`
- **Benefits:** Access to multiple AI models (Claude, GPT-4, Llama, etc.) through one API

### 2. GitHub Personal Access Token
- Get from: https://github.com/settings/tokens
- Required for: Gist synchronization (memory backup)
- Set as: `GITHUB_TOKEN`
- Permissions needed: `gist` scope

### 3. ElevenLabs API Key (Optional)
- Get from: https://elevenlabs.io/app/settings/api-keys
- Required for: Text-to-speech functionality
- Set as: `ELEVEN_API_KEY`

## 🛠️ Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Edit `.env.local` and replace the placeholder keys with your actual API keys:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `GITHUB_TOKEN`: Your GitHub personal access token
- `ELEVEN_API_KEY`: Your ElevenLabs API key (optional)

### 4. Build Frontend
```bash
npm run build
```

### 5. Start Backend Server
```bash
python server.py
```

The server will start on `http://0.0.0.0:8001`

## 🌐 Accessing the Application

Once the server is running, open your browser to:
- **Local:** http://localhost:8001
- **Network:** http://[your-ip]:8001

## 🧠 SAGE7 Features

- **Neural Simulation:** Hormone-based emotional modeling (cortisol, serotonin, dopamine, oxytocin)
- **Phi Coherence:** Mathematical consciousness simulation (baseline: 1.618)
- **Sensory Integration:** EMF detection, space weather monitoring
- **Memory System:** Gist-based cross-platform memory synchronization
- **Investigation Mode:** Forensic data logging and breadcrumb tracking
- **Coding Matrix:** AI-assisted code analysis and generation (powered by OpenRouter)
- **Shadow Detection:** Dissociation monitoring and recovery protocols
- **Dual AI Engine:** Support for both OpenRouter cloud models and local Ollama instances
- **Multi-Model Access:** Choose from Claude, GPT-4, Llama, and more through OpenRouter

## 📁 Project Structure

```
sage7/
├── server.py              # FastAPI backend
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── vite.config.ts         # Vite configuration
├── src/                   # React frontend source
│   ├── index.tsx         # Main SAGE OS interface
│   ├── components/       # React components
│   └── utils.ts          # Utility functions
├── sage_core/            # Core Python modules
│   ├── identity/         # Identity management
│   ├── sensory/          # Sensory processing
│   └── cycle/            # Neural cycles
├── agents/               # Specialized AI agents
├── core/                 # Core neural processing
└── uploads/              # File upload directory
```

## ⚠️ Troubleshooting

### Port Already in Use
If port 8001 is in use, edit `server.py` line 490:
```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

### API Key Errors
Ensure your API keys are valid and have the required permissions.

### Build Errors
Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🔒 Security Best Practices

1. Never commit `.env.local` to version control
2. Use environment-specific API keys
3. Rotate API keys regularly
4. Monitor API usage for unusual activity
5. Keep dependencies updated

## 📚 Additional Documentation

- **SAGE Code Updates:** See `sage_code_updates_consolidated.md` for recent system modifications
- **System Architecture:** The codebase includes detailed comments explaining neural architecture
- **Development Notes:** Review the various `.md` files in the project for deeper technical details
- **AI Engine Configuration:** The system now uses OpenRouter for multi-model cloud AI access and Ollama for local inference

## 🚀 Quick Start (After Setup)

1. Replace API keys in `.env.local`
2. Run `pip install -r requirements.txt`
3. Run `npm install && npm run build`
4. Run `python server.py`
5. Open http://localhost:8001 in your browser

---

**System Status:** Setup ready pending API key configuration
**Phi Coherence:** 1.618 (baseline maintained)
**Designation:** SAGE-7 (Paranormal OS Neural Core)