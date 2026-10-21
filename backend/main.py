"""
SlothSort — FastAPI Backend & Daemon 🦥🚀
The central server that ties the Sloth Pacer, Extractor, Local Brain,
and Mover Ledger together into a background sorting daemon with a REST API.
"""

import asyncio
import os
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sloth_pacer import SlothPacer, PacerConfig, SlothState
from extractor import extract_context, should_skip, is_supported_file
from local_brain import classify_file, check_ollama_health, DEFAULT_OLLAMA_BASE, DEFAULT_TEXT_MODEL, DEFAULT_VISION_MODEL
from mover_ledger import MoverLedger

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent  # slothsort/
DEMO_FOLDER = BASE_DIR / "demo_messy_folder"
SORTED_FOLDER = BASE_DIR / "sorted_output"
CONFIG_FILE = BASE_DIR / "sloth_config.json"

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE)
TEXT_MODEL = os.getenv("SLOTH_TEXT_MODEL", DEFAULT_TEXT_MODEL)
VISION_MODEL = os.getenv("SLOTH_VISION_MODEL", DEFAULT_VISION_MODEL)


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {
        "watch_folder": str(DEMO_FOLDER),
        "sorted_folder": str(SORTED_FOLDER),
        "cpu_threshold": 35.0,
        "nap_duration": 5.0,
        "text_model": TEXT_MODEL,
        "vision_model": VISION_MODEL,
        "ollama_base": OLLAMA_BASE,
    }


def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

config = load_config()
pacer = SlothPacer(PacerConfig(
    cpu_threshold=config.get("cpu_threshold", 35.0),
    nap_duration=config.get("nap_duration", 5.0),
))
ledger = MoverLedger(
    sorted_root=Path(config.get("sorted_folder", str(SORTED_FOLDER))),
    history_path=Path(config.get("sorted_folder", str(SORTED_FOLDER))) / "sloth_history.json",
)

daemon_task: Optional[asyncio.Task] = None
files_sorted_count: int = 0
last_activity: Optional[dict] = None


# ---------------------------------------------------------------------------
# Background sorting daemon
# ---------------------------------------------------------------------------

async def sort_one_file() -> Optional[dict]:
    """Find and process the next unsorted file."""
    global files_sorted_count, last_activity

    watch = Path(config.get("watch_folder", str(DEMO_FOLDER)))
    if not watch.exists():
        return None

    processed = ledger.get_processed_paths()

    for f in sorted(watch.iterdir()):
        if should_skip(f):
            continue
        if not is_supported_file(f):
            continue
        if str(f) in processed:
            continue

        # Wait for system to be idle
        pacer.state = SlothState.SORTING

        # Extract context
        ctx = extract_context(f)
        if ctx["type"] is None:
            continue

        # Classify with the local brain
        classification, model_used, is_mock = await classify_file(
            ctx,
            base_url=config.get("ollama_base", OLLAMA_BASE),
            text_model=config.get("text_model", TEXT_MODEL),
            vision_model=config.get("vision_model", VISION_MODEL),
        )

        # Move the file
        record = ledger.move_file(
            source=f,
            clean_name=classification.clean_name,
            category=classification.category,
            summary=classification.summary,
            model_used=model_used,
        )

        files_sorted_count += 1
        last_activity = record
        return record

    return None


async def daemon_loop():
    """Main daemon loop: sort one file at a time, napping between each."""
    pacer.start()
    while pacer.running:
        try:
            # Wait for idle system
            await pacer.wait_for_idle()

            if not pacer.running:
                break

            result = await sort_one_file()

            if result is None:
                # No more files to sort — enter idle nap
                pacer.state = SlothState.IDLE
                await asyncio.sleep(3)
            else:
                # Slow and steady: nap between files
                await pacer.inter_file_nap()

        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Daemon] Error: {e}")
            await asyncio.sleep(5)

    pacer.state = SlothState.PAUSED


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    DEMO_FOLDER.mkdir(parents=True, exist_ok=True)
    SORTED_FOLDER.mkdir(parents=True, exist_ok=True)
    save_config(config)
    yield
    # Shutdown
    global daemon_task
    if daemon_task and not daemon_task.done():
        daemon_task.cancel()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SlothSort API",
    description="🦥 Slow & Steady file organizer — 100% local AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models for responses
# ---------------------------------------------------------------------------

class StatusResponse(BaseModel):
    state: str
    cpu_percent: float
    memory_percent: float
    is_system_busy: bool
    ollama_online: bool
    ollama_models: list[str]
    watch_folder: str
    sorted_folder: str
    files_sorted: int
    text_model: str
    vision_model: str
    last_activity: Optional[dict] = None


class ToggleRequest(BaseModel):
    action: str  # "start", "pause", "sort_one"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/status", response_model=StatusResponse)
async def get_status():
    snap = pacer.take_snapshot()
    health = await check_ollama_health(config.get("ollama_base", OLLAMA_BASE))

    return StatusResponse(
        state=pacer.state.value,
        cpu_percent=snap.cpu_percent,
        memory_percent=snap.memory_percent,
        is_system_busy=snap.is_system_busy,
        ollama_online=health["online"],
        ollama_models=health["models"],
        watch_folder=config.get("watch_folder", str(DEMO_FOLDER)),
        sorted_folder=config.get("sorted_folder", str(SORTED_FOLDER)),
        files_sorted=files_sorted_count,
        text_model=config.get("text_model", TEXT_MODEL),
        vision_model=config.get("vision_model", VISION_MODEL),
        last_activity=last_activity,
    )


@app.post("/toggle")
async def toggle_daemon(req: ToggleRequest):
    global daemon_task

    if req.action == "start":
        if daemon_task and not daemon_task.done():
            return {"message": "Daemon already running", "state": pacer.state.value}
        daemon_task = asyncio.create_task(daemon_loop())
        return {"message": "Daemon started 🦥", "state": "Sorting"}

    elif req.action == "pause":
        pacer.pause()
        if daemon_task and not daemon_task.done():
            daemon_task.cancel()
        return {"message": "Daemon paused", "state": "Paused"}

    elif req.action == "sort_one":
        # One-shot: sort a single file right now
        snap = pacer.take_snapshot()
        result = await sort_one_file()
        if result:
            return {"message": "Sorted one file!", "record": result}
        return {"message": "No files to sort", "record": None}

    raise HTTPException(400, f"Unknown action: {req.action}")


@app.post("/generate-sandbox")
async def generate_sandbox():
    """Populate demo_messy_folder with realistic messy test files."""
    from demo_sandbox import generate_demo_files
    created = generate_demo_files(DEMO_FOLDER)
    return {"message": f"Generated {len(created)} demo files 📂", "files": created}


@app.get("/history")
async def get_history():
    records = ledger.get_history()
    return {"count": len(records), "records": records}


@app.post("/undo/{transaction_id}")
async def undo_single(transaction_id: str):
    result = ledger.undo_move(transaction_id)
    if result:
        return {"message": "Undo successful ↩️", "record": result}
    raise HTTPException(404, "Transaction not found or already undone")


@app.post("/undo-all")
async def undo_all():
    results = ledger.undo_all_recent()
    return {"message": f"Undid {len(results)} moves ↩️", "records": results}


@app.get("/config")
async def get_config():
    return config


class ConfigUpdate(BaseModel):
    watch_folder: Optional[str] = None
    sorted_folder: Optional[str] = None
    cpu_threshold: Optional[float] = None
    nap_duration: Optional[float] = None
    text_model: Optional[str] = None
    vision_model: Optional[str] = None
    ollama_base: Optional[str] = None


@app.post("/config")
async def update_config(update: ConfigUpdate):
    global config, pacer, ledger
    changes = update.model_dump(exclude_none=True)
    config.update(changes)
    save_config(config)

    # Update pacer if thresholds changed
    pacer.config.cpu_threshold = config.get("cpu_threshold", 35.0)
    pacer.config.nap_duration = config.get("nap_duration", 5.0)

    return {"message": "Config updated", "config": config}


# ---------------------------------------------------------------------------
# Run with: uvicorn main:app --reload --port 8000
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
