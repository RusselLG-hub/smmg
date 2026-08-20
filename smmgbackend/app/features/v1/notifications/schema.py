from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class InAppNotification(BaseModel):
    id: str
    title: str
    message: str
    kind: Literal["appointment", "reminder", "status"]
    created_at: datetime
    href: str

