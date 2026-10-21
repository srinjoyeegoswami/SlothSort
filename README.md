<p align="center">
  <span style="font-size: 72px">🦥</span>
</p>

<h1 align="center">SlothSort</h1>
<p align="center"><strong>Slow & Steady file organizer — 100% local, AI-powered, resource-aware</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-100%25%20Local-22c55e?style=flat-square" />
  <img src="https://img.shields.io/badge/Cloud%20Data-Zero%20Bytes-f59e0b?style=flat-square" />
  <img src="https://img.shields.io/badge/Hackathon-Slow%20%26%20Steady-purple?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" />
</p>

---

## 🦥 What is SlothSort?

**SlothSort** is an open-source, 100% local, resource-aware file organizer that uses AI to tame your messy `Downloads` folder — without ever sending a single byte to the cloud.

It runs quietly in the background like a literal sloth:
- **Checks CPU load** before doing any AI work (never lags your laptop)
- **Processes one file at a time** with naps in between ("Slow and Steady")
- **Uses local open-weight models** via Ollama for understanding files
- **Renames files cleanly** and sorts them into categorized folders
- **Maintains a 1-click "Lazy Undo"** ledger to reverse any action

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **Dual-Model AI** | `llama3.2:3b` for text/documents, `moondream` for screenshots |
| 🏠 **100% Local** | All inference runs on `localhost:11434` via Ollama |
| 📊 **Sloth Pacer** | CPU/RAM monitoring — only works when your machine is idle |
| 📂 **Smart Categories** | Finance, Study, Code, Media, Personal, Misc |
| ↩️ **Lazy Undo** | Revert any or all sorted files with one click |
| 🎨 **Cozy Dashboard** | Dark-mode React UI with live CPU meter and activity feed |
| 🧪 **Demo Sandbox** | Generate fake messy files instantly for safe testing |
| 🔒 **Zero Cloud** | Your bank statements and screenshots never leave your laptop |

## 🏗️ Architecture

```
slothsort/
├── backend/
│   ├── main.py              # FastAPI server + daemon lifecycle
│   ├── sloth_pacer.py        # CPU/Memory monitor & sleep scheduler
│   ├── extractor.py          # PDF/text/image content extractor
│   ├── local_brain.py        # Ollama API client + structured JSON
│   ├── mover_ledger.py       # Safe mover + Undo ledger
│   ├── demo_sandbox.py       # Messy file generator
│   └── requirements.txt
├── frontend/
│   └── React + Vite + Tailwind dashboard
├── demo_messy_folder/         # Auto-generated test files
├── sorted_output/             # Where clean files end up
├── SUBMISSION_POST.md
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Ollama** ([install from ollama.com](https://ollama.com))

### 1. Pull the AI models
```bash
ollama pull llama3.2:3b
ollama pull moondream
```

### 2. Start the backend
```bash
cd slothsort/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Start the frontend
```bash
cd slothsort/frontend
npm install
npm run dev
```

### 4. Open the dashboard
Navigate to **http://localhost:5173** and:
1. Click **"Generate Messy Demo Folder"** to create safe test files
2. Click **"Start Sorting"** to watch the sloth organize them
3. Use **"Undo"** buttons on any card to revert a sort

## 🎛️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SLOTH_TEXT_MODEL` | `llama3.2:3b` | Local text/document model |
| `SLOTH_VISION_MODEL` | `moondream` | Local vision/screenshot model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |

CPU threshold and nap duration are configurable via the API at `POST /config`.

## 🔒 Privacy by Design

SlothSort processes **bank statements, IDs, private screenshots, tax forms, and personal documents** that live in your Downloads folder. This is why 100% local inference isn't just a feature — it's the entire point:

- ✅ **Zero bytes leave your laptop** — all inference on `localhost`
- ✅ **No API keys required** — no monthly token bill
- ✅ **Works offline** — sort files on a plane or train
- ✅ **Hot-swap models** — use whatever fits your RAM

## 📜 License

MIT — do whatever you want with it. Happy sorting! 🦥
