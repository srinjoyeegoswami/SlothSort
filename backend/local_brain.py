"""
SlothSort — The Local Brain 🧠
Routes files to Ollama's local models for AI-powered categorization.
Text/PDF → llama3.2:3b  |  Images → moondream
Uses structured JSON schema output for reliable parsing.
Includes a graceful mock/dry-run fallback when Ollama isn't available.
"""

import json
import hashlib
import httpx
from typing import Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Structured output schema
# ---------------------------------------------------------------------------

VALID_CATEGORIES = [
    "Finance_And_Bills",
    "Study_And_Papers",
    "Code_And_Tech",
    "Screenshots_And_Media",
    "Personal_And_Docs",
    "Misc_Archive",
]

class SlothClassification(BaseModel):
    clean_name: str = Field(
        ...,
        description="Lowercase snake_case, descriptive, max 5 words, WITHOUT file extension",
    )
    category: str = Field(
        ...,
        description=f"One of: {VALID_CATEGORIES}",
    )
    summary: str = Field(
        ...,
        description="Punchy 1-sentence explanation of the file contents",
    )
    confidence: int = Field(
        ..., ge=1, le=100,
        description="Confidence score from 1 to 100",
    )

# JSON schema for Ollama's `format` parameter
CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "clean_name": {"type": "string"},
        "category": {"type": "string", "enum": VALID_CATEGORIES},
        "summary": {"type": "string"},
        "confidence": {"type": "integer", "minimum": 1, "maximum": 100},
    },
    "required": ["clean_name", "category", "summary", "confidence"],
}


# ---------------------------------------------------------------------------
# Default config
# ---------------------------------------------------------------------------

DEFAULT_OLLAMA_BASE = "http://localhost:11434"
DEFAULT_TEXT_MODEL = "llama3.2:3b"
DEFAULT_VISION_MODEL = "moondream"


# ---------------------------------------------------------------------------
# Ollama health check
# ---------------------------------------------------------------------------

async def check_ollama_health(base_url: str = DEFAULT_OLLAMA_BASE) -> dict:
    """Check if Ollama is reachable and list available models."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                model_names = [m.get("name", "") for m in data.get("models", [])]
                return {
                    "online": True,
                    "models": model_names,
                    "url": base_url,
                }
    except Exception:
        pass
    return {"online": False, "models": [], "url": base_url}


# ---------------------------------------------------------------------------
# Mock fallback (dry-run mode)
# ---------------------------------------------------------------------------

def _mock_classify(filename: str) -> SlothClassification:
    """Deterministic mock classification when Ollama is offline."""
    name_lower = filename.lower()
    
    if any(kw in name_lower for kw in ["invoice", "receipt", "bill", "tax", "bank"]):
        cat = "Finance_And_Bills"
        summary = "Likely a financial document (mock mode — Ollama offline)."
    elif any(kw in name_lower for kw in ["lecture", "notes", "paper", "study", "essay", "thesis"]):
        cat = "Study_And_Papers"
        summary = "Appears to be study material (mock mode — Ollama offline)."
    elif any(kw in name_lower for kw in ["screenshot", "photo", "img", "image", "screen"]):
        cat = "Screenshots_And_Media"
        summary = "A screenshot or image file (mock mode — Ollama offline)."
    elif any(kw in name_lower for kw in [".py", ".js", ".ts", ".json", "code", "config", "api"]):
        cat = "Code_And_Tech"
        summary = "Looks like a code or config file (mock mode — Ollama offline)."
    else:
        cat = "Misc_Archive"
        summary = "Unrecognised file type (mock mode — Ollama offline)."

    # Deterministic name from hash
    h = hashlib.md5(filename.encode()).hexdigest()[:6]
    clean = filename.rsplit(".", 1)[0].lower()
    clean = clean.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
    # Truncate to ~5 words worth
    parts = [p for p in clean.split("_") if p][:5]
    clean_name = "_".join(parts) if parts else f"file_{h}"

    return SlothClassification(
        clean_name=clean_name,
        category=cat,
        summary=summary,
        confidence=30,
    )


# ---------------------------------------------------------------------------
# Live Ollama inference
# ---------------------------------------------------------------------------

TEXT_PROMPT_TEMPLATE = """You are a file organizer. Analyze this file and return a JSON classification.

Filename: {filename}
Content preview:
---
{snippet}
---

Rules:
- clean_name: lowercase snake_case, descriptive, max 5 words, NO file extension
- category: MUST be one of: Finance_And_Bills, Study_And_Papers, Code_And_Tech, Screenshots_And_Media, Personal_And_Docs, Misc_Archive
- summary: 1 punchy sentence describing the file
- confidence: 1-100

Return ONLY valid JSON."""


IMAGE_PROMPT = """You are a file organizer. Look at this image and return a JSON classification.

Rules:
- clean_name: lowercase snake_case, descriptive, max 5 words, NO file extension
- category: MUST be one of: Finance_And_Bills, Study_And_Papers, Code_And_Tech, Screenshots_And_Media, Personal_And_Docs, Misc_Archive
- summary: 1 punchy sentence describing what you see
- confidence: 1-100

Return ONLY valid JSON."""


async def classify_text(
    filename: str,
    snippet: str,
    base_url: str = DEFAULT_OLLAMA_BASE,
    model: str = DEFAULT_TEXT_MODEL,
) -> SlothClassification:
    """Send a text/PDF snippet to the local text model."""
    prompt = TEXT_PROMPT_TEMPLATE.format(filename=filename, snippet=snippet)

    payload = {
        "model": model,
        "prompt": prompt,
        "format": CLASSIFICATION_SCHEMA,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 256},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("response", "{}")
            parsed = json.loads(raw)
            return SlothClassification(**parsed)
    except Exception as e:
        # If JSON parsing or validation fails, try to salvage
        print(f"[LocalBrain] Text inference error: {e}")
        return _mock_classify(filename)


async def classify_image(
    filename: str,
    image_b64: str,
    base_url: str = DEFAULT_OLLAMA_BASE,
    model: str = DEFAULT_VISION_MODEL,
) -> SlothClassification:
    """Send a base64 image to the local vision model."""
    payload = {
        "model": model,
        "prompt": IMAGE_PROMPT,
        "images": [image_b64],
        "format": CLASSIFICATION_SCHEMA,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 256},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("response", "{}")
            parsed = json.loads(raw)
            return SlothClassification(**parsed)
    except Exception as e:
        print(f"[LocalBrain] Vision inference error: {e}")
        return _mock_classify(filename)


async def classify_file(context: dict, base_url: str = DEFAULT_OLLAMA_BASE,
                         text_model: str = DEFAULT_TEXT_MODEL,
                         vision_model: str = DEFAULT_VISION_MODEL,
                         ) -> tuple[SlothClassification, str, bool]:
    """
    Master dispatcher.  Returns (classification, model_used, is_mock).
    `context` is the dict returned by extractor.extract_context().
    """
    health = await check_ollama_health(base_url)

    if not health["online"]:
        return _mock_classify(context["filename"]), "mock_fallback", True

    ft = context["type"]

    if ft in ("text", "pdf") and context.get("snippet"):
        used = text_model
        if used not in health["models"]:
            # Model not pulled yet — fall back
            return _mock_classify(context["filename"]), "mock_fallback", True
        cls = await classify_text(
            context["filename"], context["snippet"], base_url, text_model
        )
        return cls, used, False

    if ft == "image" and context.get("image_b64"):
        used = vision_model
        if used not in health["models"]:
            return _mock_classify(context["filename"]), "mock_fallback", True
        cls = await classify_image(
            context["filename"], context["image_b64"], base_url, vision_model
        )
        return cls, used, False

    return _mock_classify(context["filename"]), "mock_fallback", True
