# AI Document Workflow Platform

A full-stack web application for uploading PDF documents, extracting text, searching and filtering content, and managing a role-based review workflow. Built with FastAPI and React, the platform demonstrates secure authentication, document lifecycle management, and a clean layered backend architecture suitable for portfolio and interview discussions.

---

## Main Features

The following capabilities are **implemented and verified** in the current codebase:

| Milestone | Feature |
|---|---|
| 1 | User registration and login with JWT authentication |
| 2 | Secure PDF upload with validation, local file storage, and text extraction |
| 3 | Role-based document review and approval workflow with audit history |
| 4 | Keyword search, filtering by status and upload date, sorting, and pagination |

**Additional implemented details:**

- Protected REST API with bearer-token authentication
- Document detail view with extracted text and page count
- Reviewer queue for documents awaiting approval
- Status transition history with comments (required on rejection)
- User-specific document isolation (owners see only their documents; reviewers see pending items across users)

---



## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Frontend | React, TypeScript, Vite |
| Database | SQLite |
| Authentication | JWT (`python-jose`), bcrypt password hashing |
| PDF processing | pypdf |
| Testing | Pytest, httpx |
| API docs | FastAPI OpenAPI (Swagger UI) |

---

## Application Architecture

The application follows a classic three-tier layout: a React SPA communicates with a FastAPI backend over HTTPS-ready REST endpoints, backed by a SQLite database.

```text
┌─────────────────────────────────────────────────────────────┐
│                    React SPA (Vite + TypeScript)            │
│   Login · Register · Document List · Detail · Review Queue  │
└───────────────────────────┬─────────────────────────────────┘
                            │  REST + JWT (Bearer token)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│  ┌──────────┐   ┌────────────┐   ┌──────────────────────┐  │
│  │  api/    │ → │ services/  │ → │ repositories/        │  │
│  │  routes  │   │ business   │   │ data access          │  │
│  └──────────┘   │ logic      │   └──────────┬───────────┘  │
│                 └────────────┘              │               │
│  ┌──────────┐   ┌────────────┐              │               │
│  │ schemas/ │   │ utils/     │              ▼               │
│  │ Pydantic │   │ security,  │   SQLAlchemy ORM → SQLite    │
│  └──────────┘   │ storage    │                              │
│                 └────────────┘                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   Local filesystem (uploads/)
```

**Backend layers:**

- **`api/`** — HTTP routes, request validation, and dependency injection
- **`services/`** — Business rules, workflow transitions, and PDF handling
- **`repositories/`** — Database queries (parameterized via SQLAlchemy)
- **`models/`** — SQLAlchemy ORM entities
- **`schemas/`** — Pydantic request/response models

---

## Project Folder Structure

```text
ai-document-workflow/
├── backend/
│   ├── alembic/                 # Database migration scripts
│   │   └── versions/
│   ├── app/
│   │   ├── api/                 # FastAPI route modules
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/      # Data access layer
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── utils/               # Security and file storage helpers
│   │   ├── config.py            # Environment-based settings
│   │   ├── database.py          # Engine and session setup
│   │   ├── dependencies.py      # Auth dependencies
│   │   └── main.py              # Application entry point
│   ├── scripts/
│   │   └── seed_reviewer.py     # Local reviewer account seeder
│   ├── tests/                   # Pytest test suite
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # HTTP client and API calls
│   │   ├── components/          # Reusable UI components
│   │   ├── hooks/               # React context hooks
│   │   ├── pages/               # Route-level page components
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx
│   ├── .env.example
│   └── package.json
├── uploads/                     # Stored PDF files (runtime, per user)
└── README.md
```

---

## Local Installation

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- Git

### Clone the repository

```bash
git clone https://github.com/AzizAmri02/ai-document-workflow.git
cd ai-document-workflow
```

---

## Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt

# Copy environment template and adjust values
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# Apply database migrations
alembic upgrade head

# (Optional) Seed a reviewer account for local testing
python scripts/seed_reviewer.py

# Start the development server
uvicorn app.main:app --reload
```

The API is available at **http://localhost:8000**.

Interactive API documentation: **http://localhost:8000/docs**

Health check: **http://localhost:8000/health**

---

## Frontend Setup

```bash
cd frontend

npm install

# Copy environment template
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# Start the development server
npm run dev
```

The web application is available at **http://localhost:5173**.

Production build:

```bash
npm run build
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy database connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | Secret used to sign JWT tokens | *(must be changed for production)* |
| `ACCESS_TOKEN_EXPIRE_HOURS` | JWT token lifetime in hours | `24` |
| `UPLOAD_DIR` | Directory for stored PDF files | `uploads` |
| `MAX_UPLOAD_SIZE_BYTES` | Maximum upload size in bytes | `10485760` (10 MB) |
| `CORS_ORIGINS` | JSON list of allowed frontend origins | `["http://localhost:5173"]` |

> **Note:** `OPENAI_API_KEY` may appear in `.env.example` for future AI features. It is **not used** by the current application.

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

Never commit `.env` files or real secrets to version control.

---

## Database Migrations with Alembic

Alembic manages schema changes independently of application startup.

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Roll back one revision
alembic downgrade -1

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"
```

**Existing migrations:**

| Revision | Description |
|---|---|
| `001_create_users` | Users table with role enum |
| `002_create_documents` | Documents and document text tables |
| `003_create_status_history` | Status transition audit table |

On startup, the application also calls `Base.metadata.create_all()` as a convenience for local development. For production or team workflows, prefer Alembic migrations as the source of truth.

---

## How to Run Tests

### Backend

```bash
cd backend
pytest
```

With coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

**Verified result:** 27 backend tests passing.

### Frontend

```bash
cd frontend
npm run build
```

**Verified result:** Frontend production build completes successfully (`tsc --noEmit && vite build`).

---

## User Roles and Workflow

### Roles

| Role | Capabilities |
|---|---|
| **user** | Register, upload PDFs, view own documents, submit for review, resubmit rejected documents |
| **reviewer** | All user capabilities plus access to the review queue, approve/reject pending documents, view any pending document |

New accounts register with the **user** role. A **reviewer** account can be created locally with `scripts/seed_reviewer.py`.

### Document status lifecycle

```text
                    ┌─────────────────┐
                    │      draft      │
                    └────────┬────────┘
                             │  owner submits
                             ▼
                    ┌─────────────────┐
                    │ pending_review  │
                    └────────┬────────┘
                   approve / │ \ reject (comment required)
                             ▼   ▼
              ┌──────────────┐   ┌──────────────┐
              │   approved   │   │   rejected   │
              └──────────────┘   └──────┬───────┘
                                        │  owner resubmits
                                        ▼
                               draft or pending_review
```

**Transition rules (enforced in the service layer):**

| From | To | Who |
|---|---|---|
| `draft` | `pending_review` | Document owner |
| `pending_review` | `approved` | Reviewer |
| `pending_review` | `rejected` | Reviewer (comment required) |
| `rejected` | `draft` | Document owner |
| `rejected` | `pending_review` | Document owner |

Approved documents are terminal — no further transitions are allowed. Every status change is recorded in the audit history.

---

## Main API Endpoints

All document routes require a valid JWT bearer token unless noted otherwise.

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register` | Create a new user account | Public |
| `POST` | `/api/auth/login` | Obtain a JWT access token | Public |
| `GET` | `/api/auth/me` | Return the authenticated user profile | User |
| `POST` | `/api/documents/upload` | Upload a PDF (multipart form) | User |
| `GET` | `/api/documents` | List, search, filter, sort, and paginate documents | User |
| `GET` | `/api/documents/review-queue` | List documents pending review | Reviewer |
| `GET` | `/api/documents/{id}` | Get document metadata | User / Reviewer |
| `GET` | `/api/documents/{id}/text` | Get extracted text and page count | User / Reviewer |
| `PATCH` | `/api/documents/{id}/status` | Transition document status | User / Reviewer |
| `GET` | `/api/documents/{id}/history` | Get status change audit trail | User / Reviewer |
| `GET` | `/health` | Health check | Public |

### Query parameters for `GET /api/documents`

| Parameter | Description |
|---|---|
| `q` | Keyword search across title, filename, and extracted text |
| `status` | Filter by status (`draft`, `pending_review`, `approved`, `rejected`) |
| `uploaded_from` | Filter by upload date (inclusive), format `YYYY-MM-DD` |
| `uploaded_to` | Filter by upload date (inclusive), format `YYYY-MM-DD` |
| `sort` | `created_at` (newest first) or `created_at_asc` |
| `page` | Page number (default `1`) |
| `limit` | Items per page, 1–100 (default `20`) |

---

## Security Measures

The following protections are implemented and covered by automated tests:

| Measure | Implementation |
|---|---|
| Password hashing | bcrypt via `bcrypt.hashpw` / `bcrypt.checkpw` |
| Authentication | JWT bearer tokens signed with HS256 |
| Authorization | Role-based access (`user` vs `reviewer`) via FastAPI dependencies |
| Document access control | Owners can only access their own documents; reviewers can access pending documents across users |
| PDF validation | Extension (`.pdf`), MIME type, magic-byte (`%PDF`), non-empty file, and maximum size checks |
| Path traversal protection | Stored paths are resolved and constrained within the configured upload root |
| SQL injection prevention | SQLAlchemy parameterized queries throughout repositories |
| Search wildcard escaping | `%`, `_`, and `\` characters in search terms are escaped before SQL `LIKE` matching |

Additional hardening for production deployments (HTTPS, rate limiting, secret rotation) is listed under planned features.

---

## Current Project Status

| Area | Status |
|---|---|
| Milestone 1 — Authentication | Complete |
| Milestone 2 — PDF upload and extraction | Complete |
| Milestone 3 — Review workflow | Complete |
| Milestone 4 — Search, filter, sort, pagination | Complete |
| Backend test suite | **27 tests passing** |
| Frontend production build | **Successful** |
| AI summaries | Planned |
| Semantic search | Planned |
| Docker containerization | Planned |
| CI/CD pipeline | Planned |
| Production deployment | Planned |

---

## Planned Features / Roadmap

The items below are **not yet implemented** in the running application. They are planned for future milestones:

- **AI document summaries** — Generate concise summaries from extracted PDF text (OpenAI integration)
- **Semantic search** — Embedding-based search beyond keyword matching
- **Docker** — Containerized backend, frontend, and database for consistent environments
- **CI/CD** — Automated test and build pipeline (e.g. GitHub Actions)
- **Production deployment** — Hosted deployment with PostgreSQL, HTTPS, and environment-specific configuration

---

## Author

**Mohamed Aziz Amri**

- GitHub: [AzizAmri02](https://github.com/AzizAmri02)
- Repository: [github.com/AzizAmri02/ai-document-workflow](https://github.com/AzizAmri02/ai-document-workflow)

---

## License

MIT
