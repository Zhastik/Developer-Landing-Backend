import json
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List


class JsonFileStorage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_json(self, default: Any) -> Any:
        with self.lock:
            if not self.path.exists():
                return default
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return default

    def write_json(self, data: Any) -> None:
        with self.lock:
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def append_jsonl(self, item: Dict[str, Any]) -> None:
        with self.lock:
            with self.path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(item, ensure_ascii=False) + "\n")

    def read_jsonl(self) -> List[Dict[str, Any]]:
        with self.lock:
            if not self.path.exists():
                return []
            rows: List[Dict[str, Any]] = []
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return rows
