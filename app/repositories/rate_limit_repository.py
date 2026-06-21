import time
from typing import Dict, List

from app.core.config import get_settings
from app.utils.json_file import JsonFileStorage


class RateLimitRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self.storage = JsonFileStorage(settings.data_path / "ratelimit.json")

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        data: Dict[str, List[float]] = self.storage.read_json(default={})

        window_start = now - window_seconds
        timestamps = [ts for ts in data.get(key, []) if ts >= window_start]

        if len(timestamps) >= limit:
            data[key] = timestamps
            self.storage.write_json(data)
            return False

        timestamps.append(now)
        data[key] = timestamps
        self.storage.write_json(data)
        return True
