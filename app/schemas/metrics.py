from typing import Dict, Optional

from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_contacts: int
    ai_success: int
    ai_failures: int
    email_success: int
    email_failures: int
    by_category: Dict[str, int]
    by_sentiment: Dict[str, int]
    last_contact_at: Optional[str]
