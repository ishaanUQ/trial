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

TODO: local run and `docker compose up` instructions, filled in as part of documentation
delivery (see `docs/DELIVERY_PLAN.md`, Issue 12).

## Testing

TODO: how to run the pytest suite and coverage, filled in alongside the backend tests and
documentation delivery.

## Development tooling

Lint and type checking are configured in the root `pyproject.toml` (ruff and mypy). Dev and
test dependencies live in `requirements-dev.txt`; runtime dependencies live in
`backend/requirements.txt` and `frontend/requirements.txt`.
