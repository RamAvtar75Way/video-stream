from sqlalchemy import Column, String, Integer, ForeignKey
from app.core.database import Base


class VideoView(Base):
    __tablename__ = "video_views"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)

    watch_seconds = Column(Integer, default=0)
    last_position = Column(Integer, default=0)
