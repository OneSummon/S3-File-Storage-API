# S3 File Storage API

A RESTful API for secure file storage built with **FastAPI**, **PostgreSQL**, **Redis**, and **S3-compatible object storage** (Selectel). Supports JWT authentication, per-IP rate limiting, and async file streaming.

---

## Features

- **JWT Authentication** - registration, login, protected routes
- **File Management** - upload, download (streaming), get metadata, delete
- **S3 Storage** - files stored in S3-compatible object storage (Selectel)
- **Rate Limiting** - per-IP request throttling via Redis
- **Async** - fully async stack (SQLAlchemy, aiobotocore, asyncpg)
- **Tests** - pytest-asyncio test suite with mocked S3 and Redis

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy (async) |
| Cache / Rate Limit | Redis |
| Object Storage | S3 (Selectel) via aiobotocore |
| Auth | JWT (python-jose) + bcrypt |
| Tests | pytest + pytest-asyncio + SQLite in-memory |

---

## Project Structure

```
├── app/
│   ├── core/           # Security, rate limiting, Redis, session dep
│   ├── crud/           # DB operations (auth, files)
│   ├── database/       # Engine, session, models
│   ├── dependencies/   # FastAPI dependency annotations
│   ├── routers/        # Route handlers (auth, files)
│   ├── schemas/        # Pydantic schemas
│   └── services/       # S3 client (storage_s3_selectel.py)
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_files.py
├── main.py
├── requirements.txt
└── pytest.ini
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- S3-compatible bucket (Selectel or AWS)

### Installation

```bash
git clone https://github.com/OneSummon/S3-File-Storage-API.git
cd S3-File-Storage-API
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DB_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60

# S3 / Selectel
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.selectel.ru
S3_BUCKET_NAME=your-bucket-name
S3_DOMEN_URL=https://your-bucket-name.s3.selectel.ru
```

### Run

```bash
python main.py
```

API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | - |
| POST | `/auth/login` | Login, returns JWT | - |

### Files

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/files/uploads` | Upload a file (max 5 GB) | ✅ |
| GET | `/files/all` | List your files (paginated) | ✅ |
| GET | `/files/{file_id}` | Get file metadata | ✅ |
| GET | `/files/{file_id}/download` | Stream-download a file | ✅ |
| DELETE | `/files/{file_id}` | Delete a file | ✅ |

All `/files` routes require a `Bearer` token in the `Authorization` header and are subject to rate limiting.

---

## Running Tests

Tests use an in-memory SQLite database and mock S3/Redis - no external services required.

```bash
pytest
```

Test coverage includes:

- User registration and login (success, duplicate, wrong password, non-existent user)
- File upload (authenticated and unauthenticated)
- File listing with pagination and ownership isolation
- File metadata retrieval (success, not found, forbidden, unauthenticated)
- File download with correct headers and content streaming
- File deletion (success, not found, forbidden, unauthenticated)

---

## Notes

- Files are stored with a UUID-based unique name in S3 to avoid conflicts
- File size is determined before upload and stored in the database
- Downloading streams content in 5 MB chunks to handle large files efficiently
- Rate limiting is applied per client IP and resets every 60 seconds

## Author

- OneSummon
- GitHub: [OneSummon](https://github.com/OneSummon)