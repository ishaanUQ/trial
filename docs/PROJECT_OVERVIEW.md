# Merge Sort Demo: Project Overview

## What this is

A small full-stack demo that sorts a user-supplied array with merge sort and reports how the sort performed. It exists to make algorithm behaviour concrete: a student types in an array, presses a button, and sees the sorted result alongside real numbers for time taken, comparisons made, and element moves. Nothing is animated. The value is in the measured output, not in a moving picture.

The scope is deliberately narrow. One algorithm, one page, one endpoint that matters. Everything else in the repo exists to make that one thing correct, tested, containerised, and shippable through a normal software process.

## Architecture

Two services that talk over HTTP.

The backend is a FastAPI application. It owns the merge sort engine, the input validation, and the metric collection. It exposes a health check and a single sort endpoint that takes an array and returns the sorted array plus a metrics block. The engine is a plain Python package with no web framework imports, so it can be tested on its own and trusted independently of the API around it.

The frontend is a Streamlit page. It is a thin client. The user enters an array as text, the page parses it, sends it to the backend, and renders whatever comes back. It holds no sorting logic. If the backend rejects the input, the page shows the error. The backend address comes from an environment variable so the same image works locally and inside Docker Compose.

Docker Compose runs both services on a shared network. Streamlit reaches the backend by service name rather than localhost, which is the one detail people usually miss.

```
user -> Streamlit page -> POST /sort -> FastAPI -> merge sort engine
                                   <- sorted array + metrics <-
```

## The merge sort engine

Top-down recursive merge sort. Split the array in half, sort each half, merge the two sorted halves. The merge step is where the work happens and where the counters live.

Two counters matter for teaching:

Comparisons. Every time the merge step compares one element against another to decide which comes next, that is one comparison. For an array of n elements, merge sort makes on the order of n log n comparisons, and the demo lets a student see that number climb far more slowly than n squared would.

Writes, or element moves. Every time an element is placed into the merged output, that is one write. This is the honest picture of how much data shuffling the algorithm does.

The engine also reports wall-clock time using a high-resolution timer, the element count, and a verification flag confirming the output really is sorted. Wall-clock time and comparison count tell different stories on purpose. The comparison count is the theory. The wall-clock time is the theory plus constant factors, memory effects, and the interpreter. Seeing both side by side is the point.

Auxiliary space is reported as an estimate. Merge sort needs extra room proportional to the input size, unlike an in-place sort, and the demo notes that so the memory tradeoff is visible even without a profiler running.

## Input validation

The backend rejects bad input clearly rather than crashing or returning nonsense. The rules:

The payload must contain an array field. The array must be a list of numbers, integers or floats. Empty arrays are allowed and return an empty result with zero-valued metrics. Strings, nested lists, booleans dressed as numbers, and null entries are rejected. There is an upper bound on length so a single request cannot try to sort millions of elements and tie up the service. Non-finite values like infinity and NaN are rejected because they make ordering meaningless.

Validation lives in a Pydantic model, which means FastAPI documents it automatically and returns a structured error the frontend can display.

## Performance metrics returned

Every successful sort returns:

- element_count: how many numbers were sorted
- comparisons: total comparisons made during merging
- writes: total element moves into merged output
- time_ms: wall-clock duration in milliseconds
- is_sorted: verification that the output is correctly ordered
- aux_space_estimate: rough auxiliary memory used, in element-slots
- reference_n_log_n: n times log base 2 of n, so the comparison count can be read against the theoretical growth rate

## Tech stack

Backend: FastAPI, Uvicorn, Pydantic. Standard library for the sort itself so operation counts stay honest.

Frontend: Streamlit, plus httpx to call the backend.

Testing: pytest, pytest-cov for coverage, hypothesis for property-based tests that prove correctness across thousands of random inputs.

Quality: ruff for lint and format, mypy for type checking.

Infrastructure: Docker, Docker Compose, GitHub Actions for CI and image builds.

## Success criteria

Functional:

- A user enters an array on one page, presses sort, and sees the sorted array and the metrics block.
- The backend validates input and returns a clear error for anything malformed.
- The sort is always correct, verified on every response.
- The whole system starts with a single docker compose up.

Engineering:

- The engine package imports nothing from FastAPI or Streamlit.
- Engine test coverage is above 95 percent, including property-based tests.
- CI runs lint, type check, and tests on every pull request and blocks merge on failure.
- Both images build cleanly in CI, not just on the author's machine.

Process:

- Work is tracked as GitHub issues grouped under milestones and moved across a project board.
- Every feature lands through a pull request linked to its issue, not a direct push to main.
- Documentation covers setup, architecture, and how to run the thing, so a marker can use it without asking questions.

## How the build is automated

The repo ships with three skills, three specialist subagents, and one orchestrating subagent, all under .claude. The orchestrator reads the delivery plan, creates the issues and branches, and hands each unit of work to the right specialist. The specialists lean on the matching skill for the exact patterns and reference code. The result is that a single pass, started from one prompt, produces the working project along with its issue and pull request history. See ONESHOT_PROMPT.md for the entry point and PREFLIGHT.md for what you need running first.
