"""Structured memory store for kadiya personal assistant."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


class MemoryStore:
    """JSON-backed structured memory with tasks, reminders, notes, followups, contacts, finance."""

    SCHEMA = {
        "tasks": [],
        "reminders": [],
        "notes": [],
        "followups": [],
        "contacts": [],
        "finance": [],
    }

    def __init__(self, workspace: Path):
        self.path = workspace / "memory" / "store.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, list] = self._load()

    def _load(self) -> dict[str, list]:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                for key in self.SCHEMA:
                    if key not in data:
                        data[key] = []
                return data
            except (json.JSONDecodeError, KeyError):
                pass
        return {k: list(v) for k, v in self.SCHEMA.items()}

    def _save(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- Tasks ---
    def add_task(self, title: str, due_at: str | None = None, priority: str = "normal") -> dict:
        task = {
            "id": _new_id(),
            "title": title,
            "status": "pending",
            "due_at": due_at,
            "priority": priority,
            "created_at": _now(),
            "completed_at": None,
        }
        self._data["tasks"].append(task)
        self._save()
        return task

    def complete_task(self, task_id: str) -> dict | None:
        for t in self._data["tasks"]:
            if t["id"] == task_id or t["title"].lower().startswith(task_id.lower()):
                t["status"] = "completed"
                t["completed_at"] = _now()
                self._save()
                return t
        return None

    def list_tasks(self, status: str = "pending") -> list[dict]:
        return [t for t in self._data["tasks"] if t["status"] == status]

    def today_tasks(self) -> list[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [
            t for t in self._data["tasks"]
            if t["status"] == "pending" and (t.get("due_at") or "").startswith(today)
        ]

    # --- Reminders ---
    def add_reminder(self, text: str, trigger_type: str, trigger_value: str) -> dict:
        reminder = {
            "id": _new_id(),
            "text": text,
            "trigger": {"type": trigger_type, "value": trigger_value},
            "created_at": _now(),
            "last_triggered_at": None,
        }
        self._data["reminders"].append(reminder)
        self._save()
        return reminder

    def list_reminders(self) -> list[dict]:
        return self._data["reminders"]

    def remove_reminder(self, reminder_id: str) -> bool:
        before = len(self._data["reminders"])
        self._data["reminders"] = [r for r in self._data["reminders"] if r["id"] != reminder_id]
        if len(self._data["reminders"]) < before:
            self._save()
            return True
        return False

    # --- Notes ---
    def add_note(self, content: str, tags: list[str] | None = None) -> dict:
        note = {
            "id": _new_id(),
            "content": content,
            "tags": tags or [],
            "created_at": _now(),
        }
        self._data["notes"].append(note)
        self._save()
        return note

    def search_notes(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            n for n in self._data["notes"]
            if q in n["content"].lower() or q in " ".join(n.get("tags", [])).lower()
        ]

    def list_notes(self, tag: str | None = None) -> list[dict]:
        if tag:
            return [n for n in self._data["notes"] if tag.lower() in [t.lower() for t in n.get("tags", [])]]
        return self._data["notes"]

    # --- Follow-ups ---
    def add_followup(self, subject: str, action: str, due_at: str | None = None, linked_task_id: str | None = None) -> dict:
        followup = {
            "id": _new_id(),
            "subject": subject,
            "action": action,
            "due_at": due_at,
            "linked_task_id": linked_task_id,
            "created_at": _now(),
        }
        self._data["followups"].append(followup)
        self._save()
        return followup

    def list_followups(self) -> list[dict]:
        return self._data["followups"]

    def remove_followup(self, followup_id: str) -> bool:
        before = len(self._data["followups"])
        self._data["followups"] = [f for f in self._data["followups"] if f["id"] != followup_id]
        if len(self._data["followups"]) < before:
            self._save()
            return True
        return False

    # --- Contacts ---
    def add_contact(self, reference: str, context: str, important_dates: list[str] | None = None, notes: str = "") -> dict:
        contact = {
            "id": _new_id(),
            "reference": reference,
            "context": context,
            "important_dates": important_dates or [],
            "notes": notes,
        }
        self._data["contacts"].append(contact)
        self._save()
        return contact

    def list_contacts(self) -> list[dict]:
        return self._data["contacts"]

    # --- Finance ---
    def add_finance(self, entry_type: str, name: str, amount: float | None = None, expected_date: str | None = None, notes: str = "") -> dict:
        entry = {
            "id": _new_id(),
            "type": entry_type,
            "name": name,
            "amount": amount,
            "expected_date": expected_date,
            "notes": notes,
            "created_at": _now(),
        }
        self._data["finance"].append(entry)
        self._save()
        return entry

    def list_finance(self, entry_type: str | None = None) -> list[dict]:
        if entry_type:
            return [f for f in self._data["finance"] if f["type"] == entry_type]
        return self._data["finance"]

    # --- Utilities ---
    def forget_last(self, section: str | None = None) -> bool:
        sections = [section] if section else list(self.SCHEMA.keys())
        removed = False
        for s in sections:
            if s in self._data and self._data[s]:
                self._data[s].pop()
                removed = True
        if removed:
            self._save()
        return removed

    def forget_all(self) -> None:
        self._data = {k: [] for k in self.SCHEMA}
        self._save()

    def export_all(self) -> str:
        return json.dumps(self._data, indent=2, ensure_ascii=False)

    def get_summary(self) -> dict[str, int]:
        return {k: len(v) for k, v in self._data.items()}
