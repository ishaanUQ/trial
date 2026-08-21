# Streamlit page: array input, sort button, sorted output, metrics table.
#
# Issue 7 (feature/frontend-page): builds the static page and wires a basic
# call to the backend's POST /sort endpoint. The backend URL is a simple
# module-level constant for now; reading it from an environment variable and
# handling connection/parse/validation errors explicitly is Issue 8's job
# (feature/frontend-integration), per docs/DELIVERY_PLAN.md and the
# streamlit-static-ui skill.

import httpx
import streamlit as st

BACKEND_URL = "http://localhost:8000"

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
