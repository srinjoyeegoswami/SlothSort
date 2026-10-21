"""
SlothSort — Context Extractor 📄🖼️
Extracts just enough context from each file for the Local Brain to categorize it.
Text files → first 1 000 chars.  PDFs → page-1 text.  Images → resized base64.
"""

import base64
import io
from pathlib import Path
from typing import Optional

from PIL import Image

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEXT_EXTENSIONS = {".txt", ".md", ".py", ".json", ".csv", ".js", ".ts", ".jsx",
                   ".tsx", ".html", ".css", ".yaml", ".yml", ".toml", ".ini",
                   ".cfg", ".log", ".sh", ".bat", ".ps1", ".rb", ".go", ".rs",
                   ".java", ".c", ".cpp", ".h", ".hpp", ".xml", ".sql"}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

PDF_EXTENSIONS = {".pdf"}

SKIP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download", ".partial"}

SNIPPET_MAX_CHARS = 1000
IMAGE_MAX_EDGE = 640

ALL_SUPPORTED = TEXT_EXTENSIONS | IMAGE_EXTENSIONS | PDF_EXTENSIONS


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def is_supported_file(path: Path) -> bool:
    """Return True if the file is one we can extract context from."""
    return path.suffix.lower() in ALL_SUPPORTED


def should_skip(path: Path) -> bool:
    """Return True for hidden files, directories, temp downloads, etc."""
    if path.name.startswith("."):
        return True
    if path.is_dir():
        return True
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    return False


def file_type(path: Path) -> Optional[str]:
    """Classify a path as 'text', 'image', 'pdf', or None."""
    ext = path.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    return None


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def extract_text_snippet(path: Path) -> str:
    """Read up to SNIPPET_MAX_CHARS from a text-like file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(SNIPPET_MAX_CHARS)
    except Exception:
        return ""


def extract_pdf_page1(path: Path) -> str:
    """Extract text from the first page of a PDF (up to SNIPPET_MAX_CHARS)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        if reader.pages:
            text = reader.pages[0].extract_text() or ""
            return text[:SNIPPET_MAX_CHARS]
    except Exception:
        pass
    return ""


def resize_and_encode_image(path: Path) -> str:
    """
    Open an image with Pillow, resize so the longest edge ≤ IMAGE_MAX_EDGE,
    and return a base64-encoded JPEG string (for Ollama vision models).
    """
    try:
        img = Image.open(path)
        img = img.convert("RGB")
        w, h = img.size
        longest = max(w, h)
        if longest > IMAGE_MAX_EDGE:
            scale = IMAGE_MAX_EDGE / longest
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return ""


def extract_context(path: Path) -> dict:
    """
    Master dispatcher. Returns a dict ready for Local Brain consumption:
      { "type": "text"|"image"|"pdf",
        "filename": str,
        "snippet": str | None,
        "image_b64": str | None }
    """
    ft = file_type(path)
    result = {
        "type": ft,
        "filename": path.name,
        "snippet": None,
        "image_b64": None,
    }

    if ft == "text":
        result["snippet"] = extract_text_snippet(path)
    elif ft == "pdf":
        result["snippet"] = extract_pdf_page1(path)
    elif ft == "image":
        result["image_b64"] = resize_and_encode_image(path)

    return result
