import os
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    BackgroundTasks,
    HTTPException
)
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.video import Video
from app.models.video_view import VideoView
from app.services.encoding_service import encode_to_hls
from app.core.video_access import check_video_access
from app.core.stream_token import create_stream_token
from app.schemas.video import (
    VideoResponse,
    VideoAnalyticsResponse,
    StreamResponse,
    UploadResponse
)

UPLOAD_DIR = "media/uploads"
HLS_DIR = "media/hls"

router = APIRouter(prefix="/videos", tags=["Videos"])

# Upload video
@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    title: str,
    is_paid: bool = False,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{current_user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    video = Video(
        title=title,
        filename=filename,
        is_paid=is_paid,
        owner_id=current_user.id
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    hls_output_dir = os.path.join(HLS_DIR, str(video.id))
    os.makedirs(hls_output_dir, exist_ok=True)

    background_tasks.add_task(
        encode_to_hls,
        file_path,
        hls_output_dir
    )

    video.hls_path = f"{video.id}/index.m3u8"
    db.commit()

    return UploadResponse(
        message="Video uploaded and encoding started",
        video_id=video.id
    )


# Start video view
@router.post("/{video_id}/view/start")
def start_view(
    video_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    view = db.query(VideoView).filter(
        VideoView.video_id == video_id,
        VideoView.user_id == current_user.id
    ).first()

    if not view:
        view = VideoView(
            video_id=video_id,
            user_id=current_user.id,
            watch_seconds=0,
            last_position=0
        )
        db.add(view)
        db.commit()

    return {"message": "View started"}


# Update view progress
@router.post("/{video_id}/view/progress")
def update_progress(
    video_id: str,
    seconds: int,
    position: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    view = db.query(VideoView).filter(
        VideoView.video_id == video_id,
        VideoView.user_id == current_user.id
    ).first()

    if not view:
        raise HTTPException(status_code=400, detail="View not started")

    view.watch_seconds = max(0, view.watch_seconds + seconds)
    view.last_position = max(0, position)

    db.commit()

    return {"message": "Progress updated"}


# Video analytics (owner only)
@router.get("/{video_id}/analytics", response_model=VideoAnalyticsResponse)
def video_analytics(
    video_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    views = db.query(VideoView).filter(
        VideoView.video_id == video_id
    ).all()

    return VideoAnalyticsResponse(
        video_id=video_id,
        total_views=len(views),
        total_watch_time_seconds=sum(v.watch_seconds for v in views)
    )


# Play video (secure + resume)
@router.get("/{video_id}/play", response_model=StreamResponse)
def play_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video or not video.hls_path:
        raise HTTPException(status_code=404, detail="Video not found")

    check_video_access(video, current_user)

    stream_token = create_stream_token(
        video_id=video.id,
        user_id=current_user.id
    )

    # Resume logic
    last_position = 0
    view = db.query(VideoView).filter(
        VideoView.video_id == video_id,
        VideoView.user_id == current_user.id
    ).first()

    if view:
        last_position = view.last_position

    return StreamResponse(
        video_id=video.id,
        title=video.title,
        secure_stream_url=(
            f"/secure-stream/{video.id}/index.m3u8?token={stream_token}"
        ),
        resume_from_seconds=last_position,
        is_paid=video.is_paid
    )
