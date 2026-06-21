from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.config import get_settings
from app.utils.json_file import JsonFileStorage


class ContactRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self.storage = JsonFileStorage(settings.data_path / "contacts.jsonl")

    def save(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            **contact_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.storage.append_jsonl(item)
        return item

    def list_all(self) -> List[Dict[str, Any]]:
        return self.storage.read_jsonl()
