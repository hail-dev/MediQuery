# 🏥 MediQuery
### AI-powered Healthcare Document Q&A using RAG

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20RDS%20%7C%20EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/pgvector-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

> Upload healthcare PDFs and ask natural language questions. MediQuery uses Retrieval-Augmented Generation (RAG) to return accurate, cited answers grounded entirely in your documents — no hallucinations, no guessing.

---

<!-- ## 📸 Demo

> 🚧 *Screenshots and demo GIF coming after deployment.* -->

<!-- Replace these with actual screenshots -->
<!--
| Upload Panel | Q&A Chat |
|---|---|
| ![Upload](docs/upload.png) | ![Chat](docs/chat.png) |
-->

---

## 🧠 How It Works

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  PDF Upload  │───▶│ Parse + Chunk│───▶│   Embedding  │───▶│  pgvector   │
│  (FastAPI)   │     │  (PyMuPDF)  │     │  (OpenAI)    │     │  (AWS RDS)  │
└──────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
                                                                     │
┌──────────────┐     ┌─────────────┐     ┌──────────────┐            │
│   Answer +   │◀───│  LLM Chain   │◀───│  Retriever  │◀───────────┘
│  Citations   │     │(GPT-4o-mini)│     │  (Top-K)     │
└──────────────┘     └─────────────┘     └──────────────┘
```

1. **Upload** — User uploads a healthcare PDF via Streamlit or the API
2. **Parse** — PyMuPDF extracts text page by page
3. **Chunk** — LangChain splits text into overlapping 500-token chunks
4. **Embed** — OpenAI `text-embedding-3-small` converts chunks to vectors
5. **Store** — Vectors are stored in pgvector (PostgreSQL) on AWS RDS; original PDF goes to S3
6. **Query** — User asks a question; it's embedded and matched against stored chunks
7. **Generate** — GPT-4o-mini receives top-K chunks + question and returns a grounded answer with citations

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI |
| **RAG Orchestration** | LangChain |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | OpenAI `text-embedding-3-small` |
| **Vector Store** | pgvector (PostgreSQL) |
| **PDF Parsing** | PyMuPDF (`fitz`) |
| **Cloud Storage** | AWS S3 |
| **Cloud Database** | AWS RDS (PostgreSQL) |
| **Deployment** | Docker + AWS EC2 |
| **Frontend** | Streamlit |
| **Testing** | Pytest |
| **Language** | Python 3.10+ |

---

## 📁 Project Structure

```
mediquery/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── routers/
│   │   ├── upload.py           # POST /api/v1/upload
│   │   └── query.py            # POST /api/v1/ask
│   ├── services/
│   │   ├── ingestion.py        # PDF parse → chunk → embed → store
│   │   └── retrieval.py        # RAG chain: retrieve → generate → cite
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   └── core/
│       ├── config.py           # Settings via pydantic-settings
│       └── database.py         # pgvector connection + init
├── frontend/
│   ├── app.py                  # Streamlit UI
│   ├── utils.py                # API call helpers
│   └── config.py               # Frontend env config
├── tests/
│   └── test_query.py           # Pytest unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- AWS account with S3 and RDS access *(or use local pgvector via Docker for development)*

---

### 1. Clone the Repository

```bash
git clone https://github.com/hail-dev/mediquery.git
cd mediquery
```

### 2. Set Up Your Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# PostgreSQL (local Docker)
DATABASE_URL=postgresql://mediquery:mediquery@localhost:5432/mediquery

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=mediquery-docs

# App
APP_ENV=development
API_KEY=your_secret_api_key
```

Also set up `frontend/.env`:

```bash
API_BASE_URL=http://localhost:8000/api/v1
API_KEY=your_secret_api_key
```

---

### 4. Start with Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts:
| Service | URL |
|---|---|
| 🖥️ Streamlit UI | http://localhost:8501 |
| ⚡ FastAPI | http://localhost:8000 |
| 📖 Swagger Docs | http://localhost:8000/docs |
| 🗄️ PostgreSQL | localhost:5432 |

---

### 5. Start Manually (Development)

```bash
# Terminal 1 — Start pgvector locally
docker run -d \
  --name mediquery-pgvector \
  -e POSTGRES_USER=mediquery \
  -e POSTGRES_PASSWORD=mediquery \
  -e POSTGRES_DB=mediquery \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Terminal 2 — Start FastAPI
uvicorn app.main:app --reload

# Terminal 3 — Start Streamlit
streamlit run frontend/app.py
```

---

## 📡 API Reference

All endpoints require an `X-API-Key` header.

### `POST /api/v1/upload`

Upload and index a healthcare PDF.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | File | PDF file (max 10MB) |

**Response:**
```json
{
  "message": "Document uploaded and indexed successfully.",
  "document_id": "3f7a1c2e-...",
  "filename": "clinical_study.pdf",
  "pages": 12,
  "chunks_stored": 87
}
```

---

### `POST /api/v1/query`

Ask a question against indexed documents.

**Request body:**
```json
{
  "question": "What are the contraindications for this medication?",
  "document_id": "3f7a1c2e-..."
}
```

> Omit `document_id` to search across **all** uploaded documents.

**Response:**
```json
{
  "question": "What are the contraindications for this medication?",
  "answer": "According to the document, contraindications include...",
  "sources": [
    {
      "content": "Patients with hepatic impairment should not...",
      "page": 4,
      "document_id": "3f7a1c2e-...",
      "filename": "clinical_study.pdf"
    }
  ]
}
```

---

### `GET /`

Health check endpoint.

```json
{ "status": "ok", "message": "MediQuery API is running" }
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## ☁️ Deployment (AWS)

<!-- > 🚧 *Full deployment guide coming soon. Below is a summary.* -->

### Architecture

```
              ┌─────────────┐
  User ─────▶│  EC2 Instance│
              │  (Docker)    │
              │  FastAPI     │
              │  Streamlit   │
              └──────┬───────┘
                     │
        ┌────────────┼──────────────┐
        ▼            ▼              ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │   S3    │  │   RDS   │  │ Secrets  │
   │  (PDFs) │  │pgvector │  │ Manager  │
   └─────────┘  └─────────┘  └──────────┘
```

### Steps (Summary)

1. Create **S3 bucket** for PDF storage
2. Provision **RDS PostgreSQL** instance with pgvector extension
3. Launch **EC2 instance** (Ubuntu, t3.small or higher)
4. SSH in, install Docker, clone repo, configure `.env`
5. Run `docker-compose up -d`
6. (Optional) Set up a domain + HTTPS via NGINX + Let's Encrypt

---

## 🔒 Security

- All endpoints protected by `X-API-Key` header authentication
- File type and size validation on upload (PDFs only, max 10MB)
- Environment variables managed via `.env` (never committed)
- AWS credentials handled via environment or IAM roles in production
- Input validation via Pydantic schemas

---

<!-- ## 🗺️ Roadmap

- [x] Phase 0 — Project setup & scaffold
- [x] Phase 1 — Core RAG backend (upload, embed, retrieve, answer)
- [x] Phase 2 — Streamlit frontend with chat UI and citations
- [ ] Phase 3 — AWS deployment (S3, RDS, EC2)
- [ ] Phase 4 — Production hardening (rate limiting, logging, tests)
- [ ] Phase 5 — Documentation polish & v1.0.0 release
- [ ] Multi-user support with document namespacing
- [ ] Support for additional file types (DOCX, TXT)
- [ ] Streaming responses for faster UX
- [ ] Admin dashboard for document management

--- -->

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feat/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Jerico Dave Hilo**
- GitHub: [@hail-dev](https://github.com/hail-dev)
- LinkedIn: [linkedin.com/in/jerico-dave-hilo](https://linkedin.com/in/jerico-dave-hilo)

---

## 🙏 Acknowledgements

- [LangChain](https://langchain.com/) — RAG orchestration
- [OpenAI](https://openai.com/) — Embeddings and LLM
- [pgvector](https://github.com/pgvector/pgvector) — Vector similarity search in PostgreSQL
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python API framework
- [Streamlit](https://streamlit.io/) — Rapid frontend for ML apps
