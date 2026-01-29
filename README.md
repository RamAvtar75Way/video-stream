# Video Streaming Backend: Ram Avtar

A robust backend system for video upload, processing (HLS/DASH), and controlled streaming, designed for video-on-demand platforms and e-learning media services.

## Features

-   **Video Upload & Processing**: Automatic background encoding of uploaded videos to HLS format for adaptive streaming.
-   **Secure Streaming**: Signed URL tokens to protect content and prevent unauthorized downloads.
-   **Access Control**:
    -   **Free Content**: Publicly accessible.
    -   **Paid Content**: Restricted to video owners and premium subscribers (`is_paid` users).
-   **Analytics**: Track view counts and watch time for video owners.
-   **Resumable Playback**: Tracks user progress and resumes playback from the last watched position.
-   **Robust Error Handling**: Standardized JSON error responses for better client-side debugging.
-   **Type Safety**: Full Pydantic integration for request/response validation and accurate API documentation.

## Tech Stack

-   **Framework**: FastAPI (Python)
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy + Alembic (Migrations)
-   **Video Processing**: FFmpeg
-   **Authentication**: JWT (JSON Web Tokens)

## Getting Started

### Prerequisites
-   Python 3.10+
-   PostgreSQL
-   **FFmpeg** (Must be installed on the system path)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd video-streaming
    ```

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    -   Update `.env` with your settings.
    
    ### Environment Variables
    
    | Variable | Description | Default / Example |
    | :--- | :--- | :--- |
    | `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/db_name` |
    | `SECRET_KEY` | Secret key for JWT token generation | `your_secret_key_here` (Change this!) |
    | `ALGORITHM` | Hashing algorithm for tokens | `HS256` |
    | `ACCESS_TOKEN_EXPIRE_MINUTES` | Key expiration time in minutes | `60` |

5.  **Run Database Migrations**:
    ```bash
    alembic upgrade head
    ```

6.  **Start the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.
    API Documentation (Swagger UI) is at `http://127.0.0.1:8000/docs`.

## Key API Endpoints

-   `POST /auth/register` - Create a new user account.
-   `POST /videos/upload` - Upload a video file (starts background encoding).
-   `GET /videos/{video_id}/play` - Get a secure HLS stream URL.
-   `GET /videos/{video_id}/analytics` - View performance metrics (Owner only).
