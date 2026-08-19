# Merge Sort Demo

A small full-stack demo that sorts a user-supplied array with merge sort and reports how the
sort performed: wall-clock time, comparisons made, element writes, and a verification that the
result is actually sorted. Nothing is animated. The value is in the measured output.

## Architecture

Two services talk over HTTP. The backend is a FastAPI application that owns the merge sort
engine, input validation, and metric collection, exposing a health check and a single `/sort`
endpoint. The frontend is a thin Streamlit page: the user enters an array as text, the page
parses it, sends it to the backend, and renders the sorted result and metrics table it gets
back. Docker Compose runs both services on a shared network, with the frontend reaching the
backend by service name. See `docs/PROJECT_OVERVIEW.md` for the full technical overview.

## Project layout

```
backend/    FastAPI app, merge sort engine, schemas, metrics
frontend/   Streamlit page
tests/      pytest suite (added with the backend tests)
```

## Setup

Requires Python 3.12. Clone the repo, then create and activate a virtual environment from the
repo root:

```bash
git clone <repo-url>
cd trial
python3.12 -m venv .venv
source .venv/bin/activate
```

Install the dev/test tooling plus both services' runtime dependencies:

```bash
pip install -r requirements-dev.txt
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

This gives you everything needed to run the app locally, run the test suite, and run ruff and
mypy, without Docker.

## Running the app

### With Docker Compose (recommended)

From the repo root:

```bash
docker compose up --build
```

This builds and starts both services on a shared network. The frontend is available at
[http://localhost:8501](http://localhost:8501) and the backend at
[http://localhost:8000](http://localhost:8000) (try `GET /health`). Inside the compose network the
frontend reaches the backend at `http://backend:8000`, set via the `BACKEND_URL` environment
variable in `docker-compose.yml`, so no extra configuration is needed.

### Running locally without Docker

With the virtual environment from Setup active, start the backend from the `backend/` directory
so `app.main:app` resolves correctly:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

In a separate terminal, start the frontend from the `frontend/` directory. Since there is no
compose network to resolve the `backend` hostname, point it at localhost explicitly:

```bash
cd frontend
BACKEND_URL=http://localhost:8000 streamlit run app.py
```

The frontend defaults to `http://localhost:8000` when `BACKEND_URL` is unset, so this step is
optional if the backend is already running on the default port, but setting it explicitly is
recommended for clarity.

## Testing

Run the full pytest suite with coverage from the repo root (the root `pyproject.toml` sets
`pythonpath = ["backend"]` so `app.*` imports resolve without extra setup):

```bash
pytest tests --cov=app --cov-report=term-missing
```

The suite covers:

- **Engine tests** (`tests/test_engine.py`): fixed merge sort cases, including empty arrays,
  single elements, duplicates, and already-sorted or reverse-sorted input.
- **Property-based tests** (via Hypothesis): generated arrays checked against invariants such as
  "the output is sorted" and "the output is a permutation of the input", to catch edge cases
  fixed examples would miss.
- **Validation tests** (`tests/test_validation.py`): input schema edge cases, such as invalid or
  malformed payloads.
- **Metrics tests** (`tests/test_metrics.py`): comparison counts, write counts, and timing are
  captured correctly.
- **API tests** (`tests/test_api.py`): `GET /health` and `POST /sort` exercised through FastAPI's
  `TestClient`.

To run lint and type checks locally, matching what CI enforces:

```bash
ruff check .
mypy backend/app
```

## Development tooling

Lint and type checking are configured in the root `pyproject.toml` (ruff and mypy). Dev and
test dependencies live in `requirements-dev.txt`; runtime dependencies live in
`backend/requirements.txt` and `frontend/requirements.txt`. All three files pin minimum
versions for the key libraries so a fresh install stays reproducible without locking out
patch releases.

## CI

Every push and pull request to `main` runs lint, type check, and the full test suite with
coverage (`.github/workflows/ci.yml`). A separate workflow builds both Docker images on every
push to `main` (`.github/workflows/docker.yml`).
