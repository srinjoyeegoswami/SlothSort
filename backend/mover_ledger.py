"""
SlothSort — Safe Mover & "Lazy Undo" Ledger 📒
Renames and moves files into categorized folders, logs every transaction,
and provides 1-click undo to restore any file to its original location.
"""

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Ledger path (lives next to the watched folder by default)
# ---------------------------------------------------------------------------

DEFAULT_HISTORY_FILE = "sloth_history.json"


class MoverLedger:
    """
    Handles safe renaming, collision-free moving, and full undo capability.
    Every move is logged to a JSON ledger file.
    """

    def __init__(self, sorted_root: Path, history_path: Optional[Path] = None):
        """
        sorted_root: The base directory where category subfolders are created.
        history_path: Path to the JSON ledger file.
        """
        self.sorted_root = sorted_root
        self.sorted_root.mkdir(parents=True, exist_ok=True)
        self.history_path = history_path or (sorted_root / DEFAULT_HISTORY_FILE)
        self._ensure_history()

    # ------------------------------------------------------------------
    # History I/O
    # ------------------------------------------------------------------

    def _ensure_history(self):
        if not self.history_path.exists():
            self.history_path.write_text("[]", encoding="utf-8")

    def _load_history(self) -> list[dict]:
        try:
            return json.loads(self.history_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_history(self, records: list[dict]):
        self.history_path.write_text(
            json.dumps(records, indent=2, default=str), encoding="utf-8"
        )

    def get_history(self) -> list[dict]:
        return self._load_history()

    def get_processed_paths(self) -> set[str]:
        """Return set of original_path strings that have already been processed."""
        return {r["original_path"] for r in self._load_history() if not r.get("undone")}

    # ------------------------------------------------------------------
    # Safe move with collision handling
    # ------------------------------------------------------------------

    def _resolve_collision(self, dest: Path) -> Path:
        """If dest exists, append _1, _2, … until a free name is found."""
        if not dest.exists():
            return dest
        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent
        counter = 1
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def move_file(
        self,
        source: Path,
        clean_name: str,
        category: str,
        summary: str,
        model_used: str,
    ) -> dict:
        """
        Move `source` into `sorted_root/category/clean_name<ext>`.
        Returns the ledger record dict.
        """
        original_ext = source.suffix
        cat_dir = self.sorted_root / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        target = cat_dir / f"{clean_name}{original_ext}"
        target = self._resolve_collision(target)

        # Perform the move
        shutil.move(str(source), str(target))

        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_path": str(source),
            "original_name": source.name,
            "new_path": str(target),
            "new_name": target.name,
            "category": category,
            "summary": summary,
            "model_used": model_used,
            "undone": False,
        }

        history = self._load_history()
        history.insert(0, record)  # newest first
        self._save_history(history)
        return record

    # ------------------------------------------------------------------
    # Undo
    # ------------------------------------------------------------------

    def undo_move(self, transaction_id: str) -> Optional[dict]:
        """
        Restore a single file to its original path & name.
        Returns the updated record or None if not found.
        """
        history = self._load_history()
        for rec in history:
            if rec["id"] == transaction_id and not rec.get("undone"):
                new_path = Path(rec["new_path"])
                original_path = Path(rec["original_path"])

                if new_path.exists():
                    # Recreate original directory if needed
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(new_path), str(original_path))
                    rec["undone"] = True
                    rec["undone_at"] = datetime.now(timezone.utc).isoformat()
                    self._save_history(history)
                    return rec
                else:
                    # File was manually moved/deleted — mark undone anyway
                    rec["undone"] = True
                    rec["undone_at"] = datetime.now(timezone.utc).isoformat()
                    rec["undo_note"] = "File not found at new_path; may have been manually moved."
                    self._save_history(history)
                    return rec
        return None

    def undo_all_recent(self, limit: int = 50) -> list[dict]:
        """Undo the most recent `limit` non-undone moves."""
        history = self._load_history()
        undone = []
        count = 0
        for rec in history:
            if count >= limit:
                break
            if not rec.get("undone"):
                result = self.undo_move(rec["id"])
                if result:
                    undone.append(result)
                    count += 1
                    # Reload history after each undo since it mutates the file
                    history = self._load_history()
        return undone
