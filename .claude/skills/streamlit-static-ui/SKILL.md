---
name: streamlit-static-ui
description: Build the static Streamlit frontend for the merge sort demo, a single page that takes an array as text input and shows the sorted result plus performance metrics. Use this skill for any frontend, page, input parsing, backend-call, or error-display work in this project. There is no animation and no visualisation. Trigger it whenever the UI, the Streamlit page, or the client side of the app is involved, even if not named directly.
---

# Streamlit Static UI

One page. The user pastes an array, presses a button, sees the sorted array and a metrics table. No animation, no charts, no session gymnastics. The page is a thin client that trusts the backend for all logic.

## Layout

```
frontend/
├── app.py
├── requirements.txt
└── Dockerfile       owned by the docker-ci-quality skill
```

## Backend address

Read the backend URL from an environment variable so the same image works locally and in Compose. Default to localhost for local runs. In Compose the value is the service name.

```python
import os
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
```

## Input parsing

Accept a comma or whitespace separated list of numbers. Parse it in the frontend into a list of floats before sending. If parsing fails, show the error and do not call the backend. This keeps obvious typos out of the network round trip while the backend still does the authoritative validation.

```python
def parse_array(text: str) -> list[float]:
    cleaned = text.replace(",", " ").split()
    return [float(token) for token in cleaned]
```

## The page

```python
# frontend/app.py
import os
import httpx
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Merge Sort Demo", layout="centered")
st.title("Merge Sort Demo")
st.write("Enter an array of numbers. The backend sorts it with merge sort and reports how the sort performed.")

raw = st.text_area("Array", value="5, 3, 8, 1, 9, 2, 7", height=100)

if st.button("Sort"):
    try:
        values = [float(t) for t in raw.replace(",", " ").split()]
    except ValueError:
        st.error("Could not parse the input. Use numbers separated by commas or spaces.")
        st.stop()

    try:
        resp = httpx.post(f"{BACKEND_URL}/sort", json={"array": values}, timeout=30.0)
    except httpx.RequestError:
        st.error("Could not reach the backend. Is it running?")
        st.stop()

    if resp.status_code == 422:
        st.error(f"The backend rejected the input: {resp.json()['detail']}")
        st.stop()
    if resp.status_code != 200:
        st.error(f"Unexpected error: {resp.status_code}")
        st.stop()

    data = resp.json()
    st.subheader("Sorted array")
    st.write(data["sorted"])

    st.subheader("Performance metrics")
    m = data["metrics"]
    st.table({
        "Elements": m["element_count"],
        "Comparisons": m["comparisons"],
        "Writes": m["writes"],
        "Time (ms)": m["time_ms"],
        "n log n reference": m["reference_n_log_n"],
        "Aux space (slots)": m["aux_space_estimate"],
        "Verified sorted": m["is_sorted"],
    })
```

## requirements.txt

streamlit and httpx, pinned at install time.

## Rules

No sorting logic in the frontend. All ordering happens on the backend. Handle three failure modes explicitly: local parse failure, backend unreachable, and backend validation rejection. Keep the page to a single view. Do not add tabs, animation, or plotting, because the brief for this demo is a static input and output page.
