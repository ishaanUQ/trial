"""API-level tests for the FastAPI app.

These exercise the live app through FastAPI's TestClient, hitting the
actual HTTP layer (routing, request parsing, pydantic validation, response
serialization) rather than calling engine or schema code directly. The
happy paths for GET /health and POST /sort are covered here, along with
every malformed-payload shape the running API should reject with a 422.
"""

import math

from app.main import app
from app.schemas import MAX_LEN
from fastapi.testclient import TestClient

client = TestClient(app)


# --- GET /health -------------------------------------------------------


def test_health_status_code():
    r = client.get("/health")
    assert r.status_code == 200


def test_health_body():
    r = client.get("/health")
    assert r.json() == {"status": "ok"}


# --- POST /sort happy paths --------------------------------------------


def test_sort_valid_array_status_code():
    r = client.post("/sort", json={"array": [3, 1, 2]})
    assert r.status_code == 200


def test_sort_valid_array_result():
    r = client.post("/sort", json={"array": [5, 3, 8, 1, 9]})
    body = r.json()
    assert body["result"] == [1, 3, 5, 8, 9]


def test_sort_metrics_block_has_all_expected_keys():
    r = client.post("/sort", json={"array": [3, 1, 2]})
    metrics = r.json()["metrics"]
    assert set(metrics.keys()) == {
        "element_count",
        "comparisons",
        "writes",
        "time_ms",
        "is_sorted",
        "aux_space_estimate",
        "reference_n_log_n",
    }


def test_sort_metrics_values_for_known_input():
    r = client.post("/sort", json={"array": [3, 1, 2]})
    metrics = r.json()["metrics"]
    assert metrics["element_count"] == 3
    assert metrics["is_sorted"] is True
    assert metrics["aux_space_estimate"] == 3
    assert metrics["comparisons"] >= 1
    assert metrics["writes"] >= 3
    assert metrics["time_ms"] >= 0.0
    assert metrics["reference_n_log_n"] == round(3 * math.log2(3), 2)


def test_sort_empty_array_status_code():
    r = client.post("/sort", json={"array": []})
    assert r.status_code == 200


def test_sort_empty_array_result():
    r = client.post("/sort", json={"array": []})
    assert r.json()["result"] == []


def test_sort_empty_array_metrics_are_zeroed():
    r = client.post("/sort", json={"array": []})
    metrics = r.json()["metrics"]
    assert metrics["element_count"] == 0
    assert metrics["comparisons"] == 0
    assert metrics["writes"] == 0
    assert metrics["is_sorted"] is True
    assert metrics["aux_space_estimate"] == 0
    assert metrics["reference_n_log_n"] == 0.0


# --- POST /sort rejects malformed payloads (422) ------------------------


def test_sort_rejects_missing_array_field():
    r = client.post("/sort", json={})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_rejects_non_numeric_entries():
    r = client.post("/sort", json={"array": [1, "two", 3]})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_rejects_boolean_entries():
    r = client.post("/sort", json={"array": [1, True, 3]})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_rejects_infinity():
    # httpx's json= helper refuses to serialize non-finite floats at all
    # (they are not valid JSON), so the raw wire bytes are sent directly
    # with the literal Infinity token, which the server's own json parser
    # accepts before pydantic's finiteness check rejects it.
    r = client.post(
        "/sort",
        content=b'{"array": [1, Infinity, 3]}',
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_rejects_nan_via_json_constant():
    r = client.post(
        "/sort",
        content=b'{"array": [1, NaN, 3]}',
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_rejects_over_length_array():
    r = client.post("/sort", json={"array": [1.0] * (MAX_LEN + 1)})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_rejects_wrong_top_level_type():
    r = client.post("/sort", json=[1, 2, 3])
    assert r.status_code == 422
    assert "detail" in r.json()


def test_sort_error_body_is_structured():
    r = client.post("/sort", json={"array": ["a", "b"]})
    detail = r.json()["detail"]
    assert isinstance(detail, list)
    assert len(detail) >= 1
    assert "loc" in detail[0]
    assert "msg" in detail[0]
