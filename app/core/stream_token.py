from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings


def create_stream_token(video_id: str, user_id: str | None):
    payload = {
        "video_id": video_id,
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=5)  # ⏱ short-lived
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_stream_token(token: str, video_id: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired stream token"
        )

    if payload.get("video_id") != video_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid stream token"
        )

    return payload
