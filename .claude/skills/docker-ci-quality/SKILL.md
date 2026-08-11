---
name: docker-ci-quality
description: Set up containerisation, testing, and CI for the merge sort demo. Covers both Dockerfiles, docker-compose, the pytest suite including hypothesis property tests, ruff and mypy configuration, and the GitHub Actions workflows for CI and image builds. Use this skill for anything about Docker, Compose, tests, coverage, linting, type checking, or GitHub Actions in this project. Trigger it whenever containers, testing, quality gates, or pipelines come up, even if not named directly.
---

# Docker, CI, and Quality

This skill owns everything that makes the project shippable and trustworthy: the containers, the test suite, the linters, and the pipelines.

## Containers

Two images, one per service, plus a compose file that wires them together on a shared network. Streamlit reaches the backend by service name, not localhost.

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
```

## Tests

The engine gets the heaviest coverage. Correctness is proven two ways: fixed cases for known behaviour, and property-based tests that assert the engine agrees with Python's built-in sorted across thousands of random inputs.

```
tests/
├── test_engine.py
├── test_metrics.py
└── test_api.py
```

```python
# tests/test_engine.py
import math
from hypothesis import given, strategies as st
from app.engine.merge_sort import merge_sort


def test_empty():
    result, c = merge_sort([])
    assert result == []
    assert c.comparisons == 0


def test_single():
    result, _ = merge_sort([42])
    assert result == [42]


def test_known_case():
    result, _ = merge_sort([5, 3, 8, 1])
    assert result == [1, 3, 5, 8]


def test_duplicates():
    result, _ = merge_sort([2, 2, 1, 2])
    assert result == [1, 2, 2, 2]


@given(st.lists(st.integers()))
def test_matches_builtin_sorted(xs):
    result, _ = merge_sort(xs)
    assert result == sorted(xs)


@given(st.lists(st.integers(), min_size=2))
def test_comparison_upper_bound(xs):
    _, c = merge_sort(xs)
    n = len(xs)
    assert c.comparisons <= n * math.ceil(math.log2(n))
```

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_sort_ok():
    r = client.post("/sort", json={"array": [3, 1, 2]})
    body = r.json()
    assert body["sorted"] == [1, 2, 3]
    assert body["metrics"]["is_sorted"] is True


def test_sort_rejects_string():
    r = client.post("/sort", json={"array": ["a", "b"]})
    assert r.status_code == 422


def test_sort_rejects_nan():
    r = client.post("/sort", json={"array": [1, "NaN"]})
    assert r.status_code == 422
```

## Quality config

Put ruff and mypy config in a root pyproject.toml. Keep it simple: ruff for lint and format, mypy for the app package.

```toml
# pyproject.toml
[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
```

## CI workflow

Runs on every push and pull request. Installs backend deps and test deps, then lint, type check, tests with coverage. Fails the job on any failure so branch protection can block the merge.

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov hypothesis ruff mypy httpx
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy backend/app
      - name: Test
        working-directory: backend
        run: pytest ../tests --cov=app --cov-report=term-missing
```

## Image build workflow

Builds both images on pushes to main, proving the containers build in a clean environment. Pushing to a registry is optional and gated behind having credentials set.

```yaml
# .github/workflows/docker.yml
name: docker
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build backend
        run: docker build -t mergesort-backend ./backend
      - name: Build frontend
        run: docker build -t mergesort-frontend ./frontend
```

## Rules

Tests import the app package, so run pytest from the backend directory or set PYTHONPATH accordingly. The property tests are the safety net, keep them. CI must fail loudly on lint, type, or test failure, otherwise branch protection is decorative. Keep the Dockerfiles minimal and pin base images to a specific Python minor version.
