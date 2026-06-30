from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChannelResponse(BaseModel):
    channel_id: int
    channel_name: str
    channel_username: str

    class Config:
        from_attributes = True

class DetectionResponse(BaseModel):
    detection_id: int
    message_id: int
    channel_id: int
    image_path: str
    detected_item: str
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    alert_id: int
    message_id: int
    channel_id: int
    message_text: Optional[str]
    alert_type: str
    is_commercial: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AlertSummaryResponse(BaseModel):
    channel_name: str
    total_alerts: int
    commercial_count: int
    organic_count: int