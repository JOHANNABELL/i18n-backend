# i18n-backend

> **Intelligent Internationalization Management System** — AI-assisted backend for centralizing, automating and governing translation file management across software development teams.

Built with **FastAPI · PostgreSQL · SQLAlchemy** — designed for production with full RBAC, atomic transactions, versioning and audit trails.

---

## Overview

Managing translation files across multiple teams is messy — texts scattered in source code, no version history, no access control, no workflow. This backend solves all of that.

It provides a structured API for:
- Organizing translations by **project** and **language**
- Controlling **who can do what** with a 4-level RBAC system
- Tracking **every change** with audit logs and version snapshots
- Automating translation generation via **LLM APIs** (OpenAI, Gemini, DeepSeek)
- Enforcing a **human validation workflow** before any AI-generated translation goes live

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python) |
| Database | PostgreSQL (Neon) |
| ORM | SQLAlchemy + Alembic |
| Validation | Pydantic |
| Testing | Pytest |
| API Docs | Swagger / OpenAPI |

---

## Architecture

```
src/
├── entities/           # SQLAlchemy ORM models (9 tables)
├── exceptions.py       # 11 custom exceptions
├── project/            # Project CRUD (models · service · controller)
├── projectMember/      # Member management with RBAC
├── translationFile/    # File operations + export + versioning
├── message/            # Message lifecycle + approval workflow
├── api.py              # Router registration
└── database/           # DB connection
tests/
├── test_message_workflow.py   # Atomic transaction tests
├── test_rbac.py               # RBAC enforcement tests
└── test_file_operations.py    # File management tests
scripts/
├── create_schema.sql          # Database migration
└── validate_schema.py         # Schema validation
```

---

## Database Schema

**8 core tables** with integrity constraints:

```
organizations       → Org info
users               → User accounts
projects            → Translation projects
project_members     → Team members with roles
translation_files   → Language-specific files
messages            → Individual translations
translation_versions → Version snapshots (JSON)
audit_logs          → Full change tracking
```

Key constraints:
- `uq_org_project_name` — one project per org name
- `uq_project_language` — one file per language per project
- `uq_file_message_key` — unique translation keys per file
- `CASCADE` delete on all foreign keys

---

## RBAC System

4-level role-based access control, enforced at **service layer** (not controller):

| Role | Read | Create/Edit | Approve/Reject | Manage Team |
|------|------|-------------|----------------|-------------|
| `VIEWER` | ✅ | ❌ | ❌ | ❌ |
| `EDITOR` | ✅ | ✅ | ❌ | ❌ |
| `LEAD` | ✅ | ✅ | ✅ | ❌ |
| `ADMIN` | ✅ | ✅ | ✅ | ✅ |

Granularity is **per project** — the same user can have different roles on different projects.

---

## Key Feature: Atomic Message Update ⭐

Every message update triggers a **single atomic transaction**:

```
1. Update message value
2. Create audit log entry
3. Increment file version counter
4. Snapshot ALL messages as JSON
5. Commit — or full rollback if any step fails
```

No orphaned versions. No missing audit trails. Ever.

---

## AI Translation Workflow

```
Source file → Extract strings → LLM API generates translations
                                        ↓
                              Saved as PENDING
                                        ↓
                       Reviewer reads, edits if needed
                                        ↓
                    APPROVED → published  |  REJECTED → discarded
```

No AI-generated translation is published without **explicit human approval**.

---

## API Endpoints

### Projects
```
POST   /projects                      Create project
GET    /projects                      List projects
GET    /projects/{id}                 Get project details
PATCH  /projects/{id}                 Update project
DELETE /projects/{id}                 Delete project
GET    /projects/{id}/stats           Project statistics
```

### Translation Files
```
POST   /projects/{id}/files           Create file
GET    /projects/{id}/files           List files
GET    /projects/{id}/files/{id}      Get file
PATCH  /projects/{id}/files/{id}      Update file
DELETE /projects/{id}/files/{id}      Delete file
GET    /projects/{id}/files/{id}/export     Export as JSON
GET    /projects/{id}/files/{id}/versions   Version history
```

### Messages
```
POST   /files/{id}/messages           Create message
GET    /files/{id}/messages           List messages
PATCH  /files/{id}/messages/{id}      Update message
POST   /files/{id}/messages/{id}/approve   Approve
POST   /files/{id}/messages/{id}/reject    Reject
DELETE /files/{id}/messages/{id}      Delete message
```

### Team Members
```
POST   /projects/{id}/members         Add member
GET    /projects/{id}/members         List members
PATCH  /projects/{id}/members/{id}    Update role
DELETE /projects/{id}/members/{id}    Remove member
```

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/JOHANNABELL/i18n-backend.git
cd i18n-backend

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL=your_postgresql_url

# Initialize database schema
python scripts/create_schema.sql

# Start the server
uvicorn src.main:app --reload
```

API available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run by module
pytest tests/test_message_workflow.py -v   # Atomic transactions
pytest tests/test_rbac.py -v               # RBAC enforcement
pytest tests/test_file_operations.py -v    # File operations
```

**Coverage:**
- ✅ Atomic transaction workflows
- ✅ RBAC enforcement (all 4 roles)
- ✅ File export / import
- ✅ Version history snapshots
- ✅ Unique constraint validation
- ✅ Error and rollback scenarios

---

## Built During

**Technical Internship — RHOPEN LABS, Douala**
December 2025 – March 2026

Part of a two-project internship focused on AI-assisted internationalization and neural machine translation for African languages.

---

## Related

- 🤗 [EN/FR ↔ Swahili Dataset](https://huggingface.co/datasets/Johannna-Bell827/fr-sw-en-sw-translation) — companion NMT dataset
- 🌐 [SCON Website](https://scon-officiel.org) — another project from this period

