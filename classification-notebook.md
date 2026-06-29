# Commercial Email Classification Notebook Testing

Use this guide after completing `classification-setup.md`.

Notebook:

```text
notebooks/email_classification_poc_testing.ipynb
```

Sample data:

```text
notebooks/data/email_classification_samples.jsonl
```

## 1. Start Required Services

Terminal 1:

```bash
ollama serve
```

Terminal 2:

```bash
uv run jupyter notebook
```

Open:

```text
notebooks/email_classification_poc_testing.ipynb
```

The FastAPI server is optional for notebook-only testing. The notebook calls Python functions directly.

## 2. Confirm the Notebook Imports

Run the first code cell.

It imports:

```python
from app.core.settings import get_settings
from app.core.dspy_config import configure_dspy
from app.classification.okf_loader import load_category_documents, load_issue_catalog
from app.classification.pipeline import run_email_classification
from app.classification.evaluation import evaluate_samples
```

It also calls:

```python
configure_dspy(settings)
```

This configures DSPy with the Ollama Qwen model from `.env`.

Expected output:

```text
ollama_chat/qwen3:8b
```

or:

```text
ollama_chat/qwen2.5vl:7b
```

depending on `.env`.

## 3. Confirm OKF Files Load

Run the second code cell:

```python
catalog = load_issue_catalog()
categories = load_category_documents()
len(categories), catalog[:300]
```

Expected:

```text
20
```

This confirms the 20 commercial banking OKF category files are available.

## 4. Run One Email First

Run only the single-example cell first:

```python
example = {
    "subject": "Change of registered mobile number",
    "body": "Hello Team, our finance manager has changed his mobile number. Please update the registered mobile number for our current account with immediate effect. The old number should no longer be used for OTP alerts or banking communication.",
}

result = run_email_classification(**example)
result.model_dump()
```

Expected result:

```text
final_category_id = CAT-002
final_category_name = Registered Phone Number Change
needs_review = false
```

Also check:

```text
candidates[0].category_id = CAT-002
```

If `processing_errors` is empty, Qwen completed the DSPy stages.

If `processing_errors` contains Ollama connection errors, the pipeline used deterministic fallback. That is useful for debugging retrieval, but not a full LLM test.

## 5. Run Batch Evaluation

Only after the single example works, run:

```python
sample_path = Path("notebooks/data/email_classification_samples.jsonl")
evaluation = evaluate_samples(sample_path)
evaluation
```

The current sample set includes:

- `EMAIL-001`: registered mobile number change, expected `CAT-002`
- `EMAIL-002`: RTGS payment status inquiry, expected `CAT-016`
- `EMAIL-003`: ambiguous communication details update, expected fallback/review behavior with `CAT-020`

Evaluation output includes:

```text
total
final_accuracy
candidate_recall
results
```

The most important early metric is:

```text
candidate_recall
```

The expected category should appear in the retrieved candidate list before tuning final classification.

## 6. Recommended Notebook Testing Flow

Use this order:

1. Run imports and DSPy configuration.
2. Confirm 20 OKF categories load.
3. Run the single phone-number example.
4. Inspect `routing_summary`.
5. Inspect `candidates`.
6. Inspect `processing_errors`.
7. Run batch evaluation.
8. Add more rows to `email_classification_samples.jsonl`.

## 7. Add a New Test Email

Append one JSONL row to:

```text
notebooks/data/email_classification_samples.jsonl
```

Example:

```json
{"email_id":"EMAIL-004","subject":"Add new authorized signatory","body":"Please add Ms. Priya Mehta as an authorized signatory for our current account.","expected_category_id":"CAT-003","difficulty":"easy","notes":"Direct authorized signatory addition request"}
```

Then rerun the batch evaluation cell.

## 8. If the Notebook Hangs

Interrupt:

```text
Kernel -> Interrupt Kernel
```

Then set `.env` to faster test values:

```env
DSPY_MAX_TOKENS=500
DSPY_TIMEOUT_SECONDS=20
DSPY_RETRY_ATTEMPTS=1
```

Restart:

```text
Kernel -> Restart Kernel
```

Run only one example before batch evaluation.

## 9. Interpreting Results

### Good Result

```text
final_category_id matches expected_category_id
needs_review is false for clear emails
candidate list includes expected category
processing_errors is empty
```

### Acceptable POC Result

```text
final_category_id is wrong
candidate list includes expected category
needs_review is true
```

This means retrieval found the right category and the classifier/validator needs tuning.

### Bad Result

```text
candidate list does not include expected category
```

Improve the OKF category file with better tags, typical phrases, examples, or related categories.

## 10. Testing Through the API Instead

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Call:

```bash
curl -X POST http://127.0.0.1:8000/classify-email \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "RTGS payment status required",
    "body": "We initiated an RTGS payment yesterday but the beneficiary has not confirmed receipt. Please confirm whether it was processed."
  }'
```

Expected:

```text
CAT-016 Payment Status Inquiry
```
