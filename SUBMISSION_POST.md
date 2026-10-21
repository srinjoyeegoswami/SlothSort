# 🦥 SlothSort — Slow & Steady Wins the File Organization Race

*Built for the "Slow and Steady" (International Sloth Day) Hackathon*

---

## The Problem We All Pretend Doesn't Exist

Let's be honest: your `Downloads` folder is a disaster.

Right now, somewhere on your laptop, there's a file called `Screenshot (482).png` sitting next to `final_v2_REAL(1).pdf`, a mystery CSV named `export_data(3)_FINAL.csv`, and a cover letter draft you swore you'd rename "later." There are 347 files in there. You haven't opened most of them since 2024. Every few months, you think about organizing them, open the folder, feel overwhelmed, and close it.

**We built SlothSort for that exact moment of laziness.**

## What is SlothSort?

**SlothSort** is a 100% local, open-source, AI-powered file organizer that embodies the sloth philosophy: *it rewards your laziness by doing the work for you while you do literally nothing.*

It runs as a background daemon that:

1. 🧠 **Understands your files** using local AI models — it reads documents, analyzes screenshots, and figures out what each file actually *is*
2. 📂 **Renames and sorts** messy files into clean, categorized folders (`Finance_And_Bills/`, `Study_And_Papers/`, `Code_And_Tech/`, etc.)
3. 💤 **Respects your computer** — it monitors CPU load and only works when your machine is idle, so it never slows you down
4. ↩️ **Offers 1-click undo** — every action is logged, and any sort can be reversed instantly

## The Open-Source Core: Why Local AI is Non-Negotiable

### Dual-Model Architecture

SlothSort uses **two local open-weight models** running via [Ollama](https://ollama.com) on `localhost:11434`:

| Model | Purpose | Size |
|-------|---------|------|
| `llama3.2:3b` | Text, PDF, code, and document analysis | ~2GB |
| `moondream` | Screenshot and image understanding | ~1.7GB |

Both models produce **structured JSON output** via Ollama's `format` parameter, ensuring reliable machine-readable classifications every time:

```json
{
  "clean_name": "acme_cloud_invoice_october",
  "category": "Finance_And_Bills",
  "summary": "Monthly invoice from Acme Cloud Services for API access and storage — $94.38 due Nov 1st.",
  "confidence": 92
}
```

### The "Sloth Pacer" — Resource-Aware Processing

The secret sauce is the **Sloth Pacer**: a CPU/RAM monitor that checks `psutil.cpu_percent()` before every file. If your laptop is busy (above 35% CPU), the sloth enters **"Nap Mode"** — it refuses to run inference until the system is idle again.

```
[Sloth Pacer] CPU at 67% — too busy. Entering Nap Mode 💤
[Sloth Pacer] CPU at 12% — idle! Processing next file... 🦥
[Sloth Pacer] Sorted: Screenshot_2026-10-19_142210.png → dashboard_revenue_chart.png
[Sloth Pacer] Inter-file nap (5s)... slow and steady.
```

Files are processed **strictly one at a time** with configurable nap durations between each. Slow and steady wins the race.

## Why Open Innovation Beats Closed Cloud APIs Here

This isn't a case where we chose open-source because it was trendy. **For this specific problem, closed cloud APIs are genuinely dangerous.**

### 🔒 Absolute Data Privacy

Your `Downloads` folder holds:
- Bank statements and tax returns
- Government IDs and passport scans
- Private screenshots (messages, medical info, salary negotiations)
- Academic papers and proprietary work documents

**Sending these automatically to a cloud API endpoint is a massive privacy risk.** With open-weight models running on `localhost:11434`, zero bytes ever leave your laptop. There's no API key to leak, no data retention policy to worry about, and no terms of service that grant training rights on your files.

### 💸 Zero Cost for 24/7 Laziness

A background daemon that runs forever shouldn't come with a monthly token bill. SlothSort uses zero API credits — the models run on your own hardware, your own electricity, at your own pace. No rate limits, no surprise invoices, no "you've exceeded your free tier."

### ✈️ Offline & Swappable

SlothSort works on a plane, on a train, in a cabin with no Wi-Fi. And because Ollama lets you hot-swap models, users can choose models based on their laptop's RAM:
- Have 8GB? Use `moondream` + `llama3.2:1b`
- Have 16GB? Use `moondream` + `llama3.2:3b` (default)
- Have 32GB? Try `llava` + `llama3.1:8b` for maximum accuracy

## The Lazy Control Panel

The React dashboard gives you a cozy, dark-mode command center:

- **Live Sloth Meter** — real-time CPU load, memory usage, and Ollama connection status
- **Activity Feed** — watch each file get renamed and sorted in real time, with the AI's 1-sentence summary
- **1-Click Undo** — every card has an instant "Undo" button to reverse the sort
- **Undo All** — panic button to revert everything at once
- **Demo Sandbox** — generate fake messy files instantly so you can test without risking real data

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Local AI | Ollama (`llama3.2:3b` + `moondream`) |
| Backend | Python, FastAPI, psutil, pypdf, Pillow, httpx |
| Frontend | React (Vite), Tailwind CSS, Lucide Icons |
| Persistence | Local JSON ledger (zero external databases) |
| Privacy | Everything on localhost — zero cloud dependency |

## Try It Yourself

```bash
# Pull the models
ollama pull llama3.2:3b
ollama pull moondream

# Start the backend
cd slothsort/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start the frontend
cd slothsort/frontend
npm install && npm run dev
```

Open **http://localhost:5173**, click "Generate Messy Demo Folder," and watch the sloth work.

---

*SlothSort: because the best kind of productivity is the kind that happens while you're napping.* 🦥
