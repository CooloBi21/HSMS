from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ActivityInfo:
    id: int
    timestamp: str
    action: str
    detail: str

    @property
    def time_display(self) -> str:
        try:
            dt = datetime.fromisoformat(self.timestamp)
            return dt.strftime("%d/%m %H:%M")
        except ValueError:
            return self.timestamp[:16] if len(self.timestamp) >= 16 else self.timestamp
