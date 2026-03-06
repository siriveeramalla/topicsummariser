## TopicSummariser (React + Django)

This project is a **PDF/Text summarizer**:

- **Frontend**: React app (`summarizer/summarizer-frontend/`)
- **Backend**: Django REST API (`summarizer/summarizerp/`)

### Features

- Upload **PDF** or paste **text**
- Returns:
  - summary
  - bullet points
  - “explain like I’m 10”
  - keywords
  - sentiment

---

## Run locally

### 1) Backend (Django)

From `summarizer/summarizerp/`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\..\requirements.txt
python manage.py runserver 8000
```

The API will be at `http://127.0.0.1:8000/api/summarize/`.

#### Environment variables (backend)

Create a `.env` (or set system env vars) using `.env.example` as reference:

- `DJANGO_DEBUG` (default `1`)
- `DJANGO_SECRET_KEY` (default is **dev-only**)
- `DJANGO_ALLOWED_HOSTS` (default `127.0.0.1,localhost`)
- `DJANGO_CORS_ALLOWED_ORIGINS` (used when `DJANGO_DEBUG=0`)
- `NLTK_AUTO_DOWNLOAD` (default `1`)

### 2) Frontend (React)

From `summarizer/summarizer-frontend/`:

```bash
npm install
npm start
```

Open `http://localhost:3000`.

#### Environment variables (frontend)

Create `summarizer/summarizer-frontend/.env`:

```bash
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

---

## API

### `POST /api/summarize/`

Accepts **either**:

- Multipart field `file` (PDF), or
- Multipart field `text` (string)

Returns:

- `{ "ok": true, "data": { ...results... } }`
- `{ "ok": false, "error": { "code": "...", "message": "..." } }`

---

## Troubleshooting

### NLTK resources missing

If your backend returns an NLTK error, run once:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### First request is slow

The first summarization request downloads/loads the HuggingFace model and can be slow.

