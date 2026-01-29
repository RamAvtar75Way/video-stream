from pydantic import BaseModel
from typing import Optional

class VideoResponse(BaseModel):
    id: str
    title: str
    filename: str
    is_paid: bool
    owner_id: str

    class Config:
        from_attributes = True

class VideoAnalyticsResponse(BaseModel):
    video_id: str
    total_views: int
    total_watch_time_seconds: int

class StreamResponse(BaseModel):
    video_id: str
    title: str
    secure_stream_url: str
    resume_from_seconds: int
    is_paid: bool

class UploadResponse(BaseModel):
    message: str
    video_id: str
