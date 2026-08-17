# Streamlit page: array input, sort button, sorted output, metrics table.
#
# Issue 7 (feature/frontend-page) built the static page and wired a basic
# call to the backend's POST /sort endpoint using a hardcoded backend URL.
#
# Issue 8 (feature/frontend-integration): reads the backend URL from the
# BACKEND_URL environment variable, matching the docker-ci-quality skill's
# compose service env, so Issue 9 can wire this up without renaming
# anything.

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
    values = [float(token) for token in raw.replace(",", " ").split()]

    try:
        resp = httpx.post(f"{BACKEND_URL}/sort", json={"array": values}, timeout=30.0)
    except httpx.RequestError:
        st.error("Could not reach the backend.")
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
