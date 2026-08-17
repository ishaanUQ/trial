# Streamlit page: array input, sort button, sorted output, metrics table.
#
# Issue 7 (feature/frontend-page) built the static page and wired a basic
# call to the backend's POST /sort endpoint using a hardcoded backend URL.
#
# Issue 8 (feature/frontend-integration): reads the backend URL from the
# BACKEND_URL environment variable (matching the docker-ci-quality skill's
# compose service env, so Issue 9 can wire this up without renaming
# anything), and handles three failure modes explicitly: local parse
# failure, backend unreachable, and backend validation rejection. Per the
# streamlit-static-ui skill, the frontend still owns no sorting logic; the
# backend is the sole authority on ordering and on validating the input.

import os

import httpx
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Merge Sort Demo", layout="centered")
st.title("Merge Sort Demo")
st.write(
    "Enter an array of numbers, separated by commas or spaces. "
    "The backend sorts it with merge sort and reports how the sort performed."
)

raw = st.text_area("Array", value="5, 3, 8, 1, 9, 2, 7", height=100)

if st.button("Sort"):
    # Failure mode 1: the input can't be parsed into numbers at all. Caught
    # locally so an obvious typo never becomes a network round trip.
    try:
        values = [float(token) for token in raw.replace(",", " ").split()]
    except ValueError as exc:
        st.error(f"Could not parse the array: {exc}")
        st.stop()

    # Failure mode 2: the backend can't be reached (connection refused,
    # timeout, DNS failure, etc).
    try:
        resp = httpx.post(f"{BACKEND_URL}/sort", json={"array": values}, timeout=30.0)
    except httpx.RequestError:
        st.error(f"Could not reach the backend at {BACKEND_URL}.")
        st.stop()

    # Failure mode 3: the backend reached the request but rejected it. The
    # 422 body has the shape {"detail": [{"type", "loc", "msg"}, ...]}; pull
    # out the human-readable msg for each entry rather than dumping the raw
    # JSON at the user, so the actual reason for the rejection is visible.
    if resp.status_code == 422:
        try:
            detail = resp.json().get("detail", [])
        except ValueError:
            detail = []
        messages = [
            entry.get("msg", str(entry)) if isinstance(entry, dict) else str(entry)
            for entry in detail
        ]
        reason = "; ".join(messages) if messages else "The backend rejected the input."
        st.error(f"The backend rejected the input: {reason}")
        st.stop()

    if resp.status_code != 200:
        st.error(f"Unexpected error from the backend: {resp.status_code}")
        st.stop()

    data = resp.json()

    st.subheader("Sorted array")
    st.write(data["result"])

    st.subheader("Performance metrics")
    m = data["metrics"]
    st.table(
        {
            "Elements": m["element_count"],
            "Comparisons": m["comparisons"],
            "Writes": m["writes"],
            "Time (ms)": m["time_ms"],
            "n log n reference": m["reference_n_log_n"],
            "Aux space (slots)": m["aux_space_estimate"],
            "Verified sorted": m["is_sorted"],
        }
    )
