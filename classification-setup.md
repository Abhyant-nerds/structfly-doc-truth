# Commercial Email Classification Setup

This guide is for a new developer who wants to run the commercial banking email classifier locally.

## 1. Prerequisites

Install these first:

- Python 3.11+
- `uv`
- Ollama

Check:

```bash
python3 --version
uv --version
ollama --version
```

## 2. Create or Sync the Virtual Environment

From the repo root:

```bash
uv sync
```

For notebook support, install the dev extras:

```bash
uv sync --extra dev
```

No extra app dependencies were added for the classifier. The OKF front matter parser uses the Python standard library, so there is no YAML package requirement.

## 3. Configure Environment Variables

Copy the example environment file if `.env` does not already exist:

```bash
cp .env.example .env
```

Default local Ollama setup:

```env
DSPY_PROVIDER=ollama_chat
DSPY_MODEL=qwen2.5vl:7b
DSPY_API_BASE=http://localhost:11434
DSPY_API_KEY=
DSPY_MODEL_TYPE=
DSPY_TEMPERATURE=0.0
DSPY_MAX_TOKENS=1200
DSPY_TIMEOUT_SECONDS=60
DSPY_RETRY_ATTEMPTS=2
```

For faster text-only classifier testing, prefer a text Qwen model:

```env
DSPY_PROVIDER=ollama_chat
DSPY_MODEL=qwen3:8b
DSPY_API_BASE=http://localhost:11434
DSPY_API_KEY=
DSPY_MODEL_TYPE=
DSPY_TEMPERATURE=0.0
DSPY_MAX_TOKENS=500
DSPY_TIMEOUT_SECONDS=20
DSPY_RETRY_ATTEMPTS=1
```

Restart the API or notebook kernel after changing `.env`.

## 4. Pull the Ollama Model

For the default repo model:

```bash
ollama pull qwen2.5vl:7b
```

For the recommended text-only test model:

```bash
ollama pull qwen3:8b
```

List installed models:

```bash
ollama list
```

Remove an old model if needed:

```bash
ollama rm qwen2.5vl:7b
```

## 5. Start Ollama

In one terminal:

```bash
ollama serve
```

Keep this terminal running.

If Ollama is already running as a background service, this command may say the port is already in use. That is fine if `localhost:11434` is responding.

Quick direct model check:

```bash
ollama run qwen3:8b
```

Or for the default model:

```bash
ollama run qwen2.5vl:7b
```

## 6. Start the API

In a second terminal from the repo root:

```bash
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
```

Expected model field:

```text
ollama_chat/<your configured DSPY_MODEL>
```

## 7. Test the Email Classifier API

In another terminal:

```bash
curl -X POST http://127.0.0.1:8000/classify-email \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "Change of registered mobile number",
    "body": "Please update the registered mobile number for our current account."
  }'
```

Expected category:

```text
CAT-002 Registered Phone Number Change
```

## 8. Start Jupyter

From the repo root:

```bash
uv run jupyter notebook
```

Open:

```text
notebooks/email_classification_poc_testing.ipynb
```

Run the cells in order. See `classification-notebook.md` for detailed notebook testing steps.

## 9. Troubleshooting

### `Connection refused`

Ollama is not reachable.

Check:

```bash
ollama serve
```

And verify `.env`:

```env
DSPY_API_BASE=http://localhost:11434
DSPY_PROVIDER=ollama_chat
DSPY_MODEL=qwen3:8b
```

### Notebook Cell Runs Too Long

Interrupt the kernel and temporarily use:

```env
DSPY_TIMEOUT_SECONDS=20
DSPY_RETRY_ATTEMPTS=1
DSPY_MAX_TOKENS=500
```

Then restart the notebook kernel.

### Model Is Too Slow

Use a text model for this classifier POC:

```bash
ollama pull qwen3:8b
```

Then set:

```env
DSPY_MODEL=qwen3:8b
```

### Stop Everything

Stop Jupyter, FastAPI, and manual Ollama processes with `Ctrl+C` in their terminals.

Check ports:

```bash
lsof -i :8000
lsof -i :8888
lsof -i :11434
```

Port meanings:

- `8000`: FastAPI
- `8888`: Jupyter
- `11434`: Ollama
