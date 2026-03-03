# S3 File Storage API

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

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

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running with Docker Compose (recommended)

**1. Clone the repository**

```bash
git clone https://github.com/OneSummon/S3-File-Storage-API.git
cd S3-File-Storage-API
```

**2. Create `.env` file**

```bash
cp .env.example .env
```

Fill in your values:

```env
# Database
POSTGRES_USER=admin
POSTGRES_PASSWORD=your-password
POSTGRES_DB=file_storage
DB_URL=postgresql+asyncpg://admin:your-password@database:5432/file_storage

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://redis:6379
MAX_REQUESTS_PER_MINUTE=60

# S3 / Selectel
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.selectel.ru
S3_BUCKET_NAME=your-bucket-name
S3_DOMEN_URL=https://your-bucket-name.s3.selectel.ru
```

> Note: use `database` and `redis` as hostnames (not `localhost`) — these are service names inside the Docker network.

**3. Build and start**

```bash
docker-compose up -d --build
```

**4. Check that everything is running**

```bash
docker-compose ps
```

API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

**Useful commands:**

```bash
docker-compose logs -f app      # view app logs in real time
docker-compose down             # stop all containers
docker-compose down -v          # stop and delete all data (including DB)
docker-compose up -d --build    # rebuild after code changes
```

---

### Running without Docker (manual)

#### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- S3-compatible bucket (Selectel or AWS)

#### Installation

```bash
git clone https://github.com/OneSummon/S3-File-Storage-API.git
cd S3-File-Storage-API
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Environment Variables

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
MAX_REQUESTS_PER_MINUTE=60

# S3 / Selectel
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.selectel.ru
S3_BUCKET_NAME=your-bucket-name
S3_DOMEN_URL=https://your-bucket-name.s3.selectel.ru
```

#### Run

```bash
python main.py
```

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
| POST | `/files/uploads` | Upload a file (max 5 GB) | Yes |
| GET | `/files/all` | List your files (paginated) | Yes |
| GET | `/files/{file_id}` | Get file metadata | Yes |
| GET | `/files/{file_id}/download` | Stream-download a file | Yes |
| DELETE | `/files/{file_id}` | Delete a file | Yes |

All `/files` routes require a `Bearer` token in the `Authorization` header and are subject to rate limiting.

---

## Running Tests

Tests use an in-memory SQLite database and mock S3/Redis - no external services required.

```bash
pytest
```

Or inside Docker:

```bash
docker-compose exec app pytest
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