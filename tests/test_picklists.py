"""
Integration tests for /api/v1/picklist_values.

This is a read-only endpoint — only GET is implemented.
POST, PUT, and DELETE should return 405 Method Not Allowed.

Bug notes:
  - When no picklist row exists in the DB, the endpoint returns
    jsonify({"error": ...}, status=404).  Due to the jsonify misuse
    throughout this codebase, this raises TypeError internally and
    Flask-RESTful returns 500 instead of the intended 404.

Tests marked @pytest.mark.bug document INTENDED behavior.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /api/v1/picklist_values
# ---------------------------------------------------------------------------

def test_get_picklist_values_success(client, sample_picklist):
    r = client.get("/api/v1/picklist_values")
    assert r.status_code == 200


def test_get_picklist_values_returns_lists_not_strings(client, sample_picklist):
    """to_dict() should split comma-separated strings into Python lists."""
    data = client.get("/api/v1/picklist_values").get_json()
    assert isinstance(data["household_relationship"], list)
    assert isinstance(data["household_relationship_type"], list)
    assert isinstance(data["household_family_side"], list)
    assert isinstance(data["card_type"], list)


def test_get_picklist_values_correct_values(client, sample_picklist):
    data = client.get("/api/v1/picklist_values").get_json()
    assert "Friend" in data["household_relationship"]
    assert "Family" in data["household_relationship"]
    assert "Colleague" in data["household_relationship"]
    assert "Holiday" in data["card_type"]
    assert "Thank You" in data["card_type"]


def test_get_picklist_values_has_version_key(client, sample_picklist):
    data = client.get("/api/v1/picklist_values").get_json()
    assert "version" in data
    assert data["version"] == 1


@pytest.mark.bug
def test_get_picklist_values_empty_db_returns_404(client):
    """Intended: 404 when no picklist record exists for version 1.
    Bug: jsonify({"error": ...}, status=404) misuse causes 500."""
    r = client.get("/api/v1/picklist_values")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Unsupported methods — Flask-RESTful returns 405 for methods not defined
# ---------------------------------------------------------------------------

def test_post_picklist_values_not_allowed(client):
    r = client.post("/api/v1/picklist_values", json={})
    assert r.status_code == 405


def test_put_picklist_values_not_allowed(client):
    r = client.put("/api/v1/picklist_values", json={})
    assert r.status_code == 405


def test_delete_picklist_values_not_allowed(client):
    r = client.delete("/api/v1/picklist_values")
    assert r.status_code == 405
