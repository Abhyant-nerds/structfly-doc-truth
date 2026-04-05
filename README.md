# StructflyDocTruth
StructflyDocTruth is a FastAPI + LangGraph pipeline for converting unstructured document text into a reviewed ground-truth record. The project uses DSPy for document-type classification and candidate-field discovery, with Ollama configured as the default local LLM backend.

## Current production-oriented setup

- Centralized environment-driven settings for app and DSPy configuration
- `dspy.configure(...)` executed once at application startup
- Ollama is the default provider, but model/provider are swappable without code changes
- Typed ingest request and response models
- Direct file ingestion using `dspy.File` for `.pdf`, `.txt`, `.docx`, and `.msg`
- Deterministic extraction fallbacks when the LLM path fails
- Health endpoint for basic operational visibility

## Configuration

Copy `.env.example` to `.env` and adjust values as needed.

```env
DSPY_PROVIDER=ollama_chat
DSPY_MODEL=qwen2.5vl:7b
DSPY_API_BASE=http://localhost:11434
DSPY_API_KEY=
DSPY_MODEL_TYPE=
DSPY_TEMPERATURE=0.0
DSPY_MAX_TOKENS=1200
DSPY_TIMEOUT_SECONDS=60
```

The active DSPy model identifier is assembled as:

```text
{DSPY_PROVIDER}/{DSPY_MODEL}
```

Examples:

- Ollama chat model: `ollama_chat/qwen2.5vl:7b`
- OpenAI-compatible local server: `openai/meta-llama/Llama-3.1-8B-Instruct`
- Hosted provider later: `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-5-20250929`, etc.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Ollama and pull a model if needed:

```bash
ollama serve
ollama pull qwen2.5vl:7b
```

Run the API:

```bash
uvicorn app.main:app --reload
```

## API

### `POST /ingest`

Request:

```json
{
  "text": "Invoice Number: INV-1001\nVendor: ABC Ltd",
  "source_type": "text"
}
```

Response shape:

```json
{
  "document_id": "doc_...",
  "source_type": "text",
  "document_type_guess": "invoice",
  "review_status": "approved",
  "raw_candidate_fields": [
    {"proposed_name": "invoice_number", "raw_value": "INV-1001"}
  ],
  "review_package": {
    "document_id": "doc_...",
    "fields": []
  },
  "ground_truth_record": {
    "document_id": "doc_...",
    "fields": []
  }
}
```

### `GET /health`

Returns service status plus the active DSPy model configuration.

### `POST /ingest-file`

Accepts a multipart file upload and passes the file directly into DSPy using `dspy.File`.

Supported file types:

- `.pdf`
- `.txt`
- `.docx`
- `.msg`

Example:

```bash
curl -X POST http://127.0.0.1:8000/ingest-file \
  -F "file=@/absolute/path/to/invoice.pdf"
```

Important:

- Uploaded files are sent to DSPy without first extracting text in the application layer.
- Runtime success depends on whether the configured model/provider supports file-native inputs.
- Text-only models may still fail on binary documents even though the API accepts them.

## Future model changes

To change models later, only update environment variables:

- Switch Ollama models: change `DSPY_MODEL`
- Switch provider families: change `DSPY_PROVIDER` and `DSPY_MODEL`
- Switch to an OpenAI-compatible endpoint: set `DSPY_PROVIDER=openai`, update `DSPY_API_BASE`, and set `DSPY_MODEL_TYPE=chat` if needed
