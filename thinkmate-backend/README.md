# ThinkMate AI — Backend

RAG + Agentic AI Socratic Learning Tutor. This is the backend-only
scaffold (Steps 1–19 of the team build order) — frontend comes later.

## What's implemented vs. stubbed

| Layer | Status |
|---|---|
| Folder structure, config, DB models, schemas | ✅ Complete |
| PDF parsing, chunking, embedding, retrieval | ✅ Complete, verified (syntax + logic tested) |
| Agent tools (question/eval/hint/threshold/weak-topic/practice/explain) | ✅ Complete |
| Agent controller (Plan-Act-Observe-Reflect) | ✅ Complete |
| API routers (documents, qa, voice, progress) | ✅ Complete |
| Prompts externalized to `prompts/*.txt` | ✅ Complete, verified loading works |
| Custom exceptions + global error handler | ✅ Complete |
| Unit tests (threshold logic, health check) | ✅ Complete — threshold tests pass via real pytest run |
| Docker Compose (backend + postgres + ollama) | ✅ Complete |
| Makefile (`make run`, `make docker-up`, `make test`) | ✅ Complete |
| STT (Whisper) | ✅ Scaffolded, Phase-4 priority |
| TTS | ⚠️ Stub only — recommend browser `speechSynthesis()` instead (see `services/tts_service.py`) |
| OCR (scanned PDFs) | ⚠️ Not implemented — `is_likely_scanned()` flags candidates for Phase 2 |

**Important — this was built and syntax/logic-tested in a sandboxed
environment without live Postgres/Ollama/HuggingFace-model-download
access.** All Python files pass `py_compile`, the DB models build real
tables via SQLAlchemy (tested against SQLite), and the pure-logic
threshold tracker was unit-verified. What has **not** been tested here:
actual LLM calls to Ollama, actual embedding model downloads, actual
ChromaDB writes. Run the smoke test below on your machine before your
first demo to catch anything environment-specific.

## Quick start

```bash
cp .env.example .env          # edit values if needed
make docker-up                # or: docker compose up -d --build
make pull-model                # first time only, ~4-5GB (llama3.1)
curl http://localhost:8000/health
```

Interactive API docs: `http://localhost:8000/docs`

Running tests: `make test` (all) or `make test-unit` (skips the
ChromaDB/Postgres-dependent integration test in `test_retrieval.py`).

## Recommended smoke test order (do this before building on top)

1. `GET /health` → confirms FastAPI + Postgres connection.
2. `POST /upload-document` with a real PDF → confirms PyMuPDF → chunker
   → embedder → ChromaDB pipeline end-to-end. Check the response's
   `chunk_count` is non-zero and sane for the file size.
3. `POST /ask-question` with that `document_id` → confirms Ollama
   connectivity and that the Socratic question is grounded in the PDF
   content (not generic).
4. `POST /submit-answer` a few times in a row → confirms hints escalate
   and the explanation reveals right at `GUIDANCE_THRESHOLD` (default 3).
5. `GET /get-progress` and `GET /weak-topics` → confirms DB writes from
   step 4 show up correctly.

If step 3 fails, it's almost always the Ollama model not pulled yet, or
`OLLAMA_HOST` pointing at the wrong hostname (`ollama` inside Docker,
`localhost` if running the backend outside Docker against a local Ollama).

## Research notes / alternatives to evaluate

These are the "most accurate for now" defaults you asked for, with the
reasoning and what to try next if you want to push quality further —
each is also inline-commented in the relevant service file.

**PDF parsing — PyMuPDF (chosen)**
Fast, accurate for digitally-generated PDFs (typed notes, slide
exports). Fails silently (near-empty text) on scanned/image PDFs —
`is_likely_scanned()` in `pdf_parser.py` flags these so you know when
to route to Tesseract OCR (Phase 2 per your scalability plan).

**Chunking — LangChain RecursiveCharacterTextSplitter (chosen)**
Splits on paragraph → sentence → word boundaries, so chunks don't cut
sentences in half — meaningfully better retrieval accuracy than naive
fixed-size splitting. If you want to push further: try
`SemanticChunker` (from `langchain_experimental`), which groups text
by meaning-similarity breakpoints rather than character count. Slower
(needs embedding calls during splitting) but often more accurate —
worth an A/B test if graded on answer quality.

**Embeddings — sentence-transformers/all-MiniLM-L6-v2 (chosen)**
Fast, CPU-friendly, "accurate enough" default, matches your original
tech stack doc. If you have GPU access and want higher retrieval
accuracy: `all-mpnet-base-v2` (bigger, ~3x slower) or
`BAAI/bge-small-en-v1.5` / `bge-base-en-v1.5` (models tuned
specifically for retrieval, often beat generic sentence-transformers
models on RAG benchmarks). Avoid OpenAI embeddings — breaks your
"fully local, no API cost" pitch.

**LLM — Ollama / Llama 3.1 (chosen, per your stack)**
`core/llm_client.py` is provider-agnostic on purpose — switching to a
HuggingFace `transformers` pipeline or a cloud endpoint (vLLM/TGI, per
your Phase-3 scalability plan) is a one-file change, not a rewrite.
If Llama 3.1 8B is too slow/heavy on your dev machines, Qwen2.5 7B or
a quantized GGUF variant (via Ollama) typically runs faster with
comparable quality for this kind of structured-output tutoring task.

**Vector DB — ChromaDB (chosen)**
Uses `PersistentClient` (not in-memory) so embeddings survive
container restarts — a very common hackathon bug where the demo
"loses" all uploaded documents after a redeploy.

## Folder structure

```
thinkmate-backend/
├── app.py                    # FastAPI entrypoint, wires routers together
├── requirements.txt
├── requirements-dev.txt       # pytest, only needed for running tests
├── pytest.ini
├── Makefile                   # make run / make docker-up / make test
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── config/settings.py        # all env-driven config, single source of truth
├── core/
│   ├── database.py           # Postgres/SQLAlchemy session management
│   ├── vectorstore.py        # ChromaDB wrapper
│   ├── llm_client.py         # Ollama wrapper (provider-agnostic)
│   └── exceptions.py         # custom exceptions + global JSON error handler
├── models/
│   ├── db_models.py          # SQLAlchemy ORM tables
│   └── schemas.py            # Pydantic request/response models
├── routers/                  # thin — one file per endpoint group
│   ├── documents.py          # POST /upload-document
│   ├── qa.py                 # POST /ask-question, /submit-answer
│   ├── voice.py               # POST /voice-input
│   └── progress.py           # GET /get-progress, /weak-topics
├── services/                 # document processing pipeline
│   ├── pdf_parser.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── retriever.py
│   ├── stt_service.py
│   └── tts_service.py
├── agent/
│   ├── agent_controller.py   # Plan-Act-Observe-Reflect loop
│   └── tools/                # one file per agent capability
│       ├── question_generator.py
│       ├── answer_evaluator.py
│       ├── hint_generator.py
│       ├── threshold_tracker.py
│       ├── weak_topic_analyzer.py
│       ├── practice_generator.py
│       └── response_formatter.py
├── prompts/                   # system prompts as editable .txt files
│   ├── socratic_question.txt
│   ├── evaluate_answer.txt
│   ├── hint.txt
│   ├── final_explanation.txt
│   └── practice_question.txt
├── tests/
│   ├── test_health.py
│   ├── test_threshold_tracker.py   # pure-logic, no deps — runs fastest
│   └── test_retrieval.py           # integration test, needs live ChromaDB
└── utils/
    ├── logger.py
    └── prompt_loader.py
```

## API endpoints (match the architecture diagram exactly)

| Method | Path | Purpose |
|---|---|---|
| POST | `/upload-document` | Upload PDF → parse, chunk, embed, index |
| POST | `/ask-question` | Start/continue a Socratic tutoring session |
| POST | `/submit-answer` | Submit answer → evaluate → hint/explain/practice |
| POST | `/voice-input` | Transcribe voice query to text (Whisper) |
| GET | `/get-progress` | Student's per-topic correct/incorrect/partial counts |
| GET | `/weak-topics` | Topics flagged as needing revision |
| GET | `/health` | Liveness check |

## Next steps for the team

1. Run the smoke test above on a real machine with Docker + Ollama.
2. Write `tests/test_retrieval.py` — standalone script hitting
   `services/retriever.py` directly (per your original build order,
   Step 9) before trusting the agent layer.
3. Once confirmed working, frontend team can mock against these exact
   request/response schemas in `models/schemas.py` without waiting on
   backend changes.
4. Add Alembic migrations once the schema stabilizes (`init_db()` via
   `create_all` is fine for hackathon dev, not for schema evolution).
