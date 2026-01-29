from sqlalchemy import Column, String, Boolean, ForeignKey
from app.core.database import Base
import uuid

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    hls_path = Column(String, nullable=True)
    is_paid = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"))
