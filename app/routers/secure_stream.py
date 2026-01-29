import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from app.core.stream_token import verify_stream_token

router = APIRouter(prefix="/secure-stream", tags=["Secure Stream"])

BASE_DIR = Path(__file__).resolve().parents[2]
HLS_DIR = BASE_DIR / "media" / "hls"


@router.get("/{video_id}/index.m3u8")
def serve_secure_playlist(video_id: str, token: str):
    # Verify token
    verify_stream_token(token, video_id)

    playlist_path = HLS_DIR / video_id / "index.m3u8"

    if not playlist_path.exists():
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Read playlist
    content = playlist_path.read_text()

    # Inject token into every segment URL
    secured_lines = []
    for line in content.splitlines():
        if line.endswith(".ts"):
            secured_lines.append(
                f"/secure-stream/{video_id}/{line}?token={token}"
            )
        else:
            secured_lines.append(line)

    secured_playlist = "\n".join(secured_lines)

    # Return rewritten playlist
    return Response(
        content=secured_playlist,
        media_type="application/vnd.apple.mpegurl",
        headers={
            "Cache-Control": "no-store",
        }
    )


@router.get("/{video_id}/{filename}")
def serve_segment(video_id: str, filename: str, token: str):
    verify_stream_token(token, video_id)

    safe_name = os.path.basename(filename)
    segment_path = HLS_DIR / video_id / safe_name

    if not segment_path.exists():
        raise HTTPException(status_code=404, detail="Segment not found")

    return FileResponse(
        segment_path,
        media_type="video/mp2t",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-store",
        }
    )
