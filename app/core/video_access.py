from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.video import Video
from app.models.user import User


def check_video_access(video: Video, user: User | None):
    # Free video → anyone can watch
    if not video.is_paid:
        return True

    # Paid video → must be logged in
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required to watch this video"
        )

    # Paid logic
    # 1. Allow if user is a paid subscriber
    if user.is_paid:
        return True

    # 2. Allow if user is the owner
    if video.owner_id == user.id:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This is a paid video. Please subscribe or log in as the owner."
    )
