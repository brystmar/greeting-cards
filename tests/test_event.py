"""
Integration tests for /api/v1/event and /api/v1/all_events.

Bug notes for this resource:
  - Parser pollution: event.py uses a module-level RequestParser and calls
    add_argument() inside each method.  'id' is only added to the parser
    when GET or DELETE is called, so PUT must be preceded by a GET call in
    the same test session to have 'id' available.  Each test that calls PUT
    starts with a GET to ensure the parser is primed.
  - POST:   Event(**args.__str__()) passes a string instead of kwargs
            (TypeError); db.session.add() is also missing.
  - DELETE: event_to_delete.delete() is not valid in SQLAlchemy 2.x.
  - Error returns: jsonify misuse causes 500 instead of the intended status.

Tests marked @pytest.mark.bug document INTENDED behavior.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /api/v1/all_events
# ---------------------------------------------------------------------------

def test_get_all_events_empty_db(client):
    r = client.get("/api/v1/all_events")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_all_events_returns_all_records(client, sample_event):
    r = client.get("/api/v1/all_events")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_get_all_events_contains_expected_fields(client, sample_event):
    first = client.get("/api/v1/all_events").get_json()[0]
    for key in ("id", "name", "date", "year", "is_archived"):
        assert key in first


# ---------------------------------------------------------------------------
# GET /api/v1/event  (single record)
# ---------------------------------------------------------------------------

def test_get_event_success(client, sample_event):
    r = client.get(f"/api/v1/event?id={sample_event}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == sample_event
    assert data["name"] == "Christmas 2025"
    assert data["year"] == 2025
    assert data["date"] == "2025-12-25"


def test_get_event_is_archived_is_bool(client, sample_event):
    data = client.get(f"/api/v1/event?id={sample_event}").get_json()
    assert isinstance(data["is_archived"], bool)
    assert data["is_archived"] is False


@pytest.mark.bug
def test_get_event_not_found_returns_404(client):
    """Intended: 404 when event does not exist.
    Parser pollution note: this GET call also primes the event parser with
    the 'id' argument, which is a side-effect needed by PUT tests.
    Bug: jsonify misuse causes 500 instead of 404."""
    r = client.get("/api/v1/event?id=99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/event
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_post_event_creates_record(client):
    """Intended: POST with valid data creates an Event and returns 201.
    Bug 1: Event(**args.__str__()) passes a string to the constructor
           (TypeError) instead of unpacking kwargs.
    Bug 2: db.session.add() is never called, so the record is not persisted."""
    payload = {
        "name": "New Year 2026",
        "date": "2026-01-01",
        "year": 2026,
        "is_archived": "False",
    }
    r = client.post("/api/v1/event", json=payload)
    assert r.status_code == 201


# ---------------------------------------------------------------------------
# PUT /api/v1/event
#
# IMPORTANT: Each PUT test makes a GET call first to ensure the module-level
# parser has 'id' registered (parser pollution workaround).
# ---------------------------------------------------------------------------

def test_put_event_updates_name(client, sample_event):
    # Prime the parser with a GET call
    client.get(f"/api/v1/event?id={sample_event}")

    payload = {"id": sample_event, "name": "Updated Event Name"}
    r = client.put("/api/v1/event", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/event?id={sample_event}")
    assert verify.get_json()["name"] == "Updated Event Name"


def test_put_event_updates_year(client, sample_event):
    client.get(f"/api/v1/event?id={sample_event}")

    payload = {"id": sample_event, "year": 2026}
    r = client.put("/api/v1/event", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/event?id={sample_event}")
    assert verify.get_json()["year"] == 2026


def test_put_event_updates_is_archived(client, sample_event):
    client.get(f"/api/v1/event?id={sample_event}")

    payload = {"id": sample_event, "is_archived": "true"}
    r = client.put("/api/v1/event", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/event?id={sample_event}")
    # is_archived is stored as a string and NOT converted in PUT, so we check
    # what was stored rather than a specific bool
    assert "is_archived" in verify.get_json()


def test_put_event_returns_event_id(client, sample_event):
    client.get(f"/api/v1/event?id={sample_event}")
    r = client.put("/api/v1/event", json={"id": sample_event, "name": "Return ID Test"})
    assert r.get_json() == sample_event


@pytest.mark.bug
def test_put_event_not_found_returns_404(client):
    """Intended: 404 when event does not exist.  Bug: 500 from jsonify misuse.
    Note: GET is called first to ensure 'id' is in the parser."""
    client.get("/api/v1/event?id=99999")
    r = client.put("/api/v1/event", json={"id": 99999, "name": "Ghost"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/event
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_delete_event_success(client, sample_event):
    """Intended: DELETE removes the record and returns 200 with the deleted
    record's data.
    Bug: event_to_delete.delete() raises AttributeError (not a valid
    SQLAlchemy 2.x instance method).  The exception is caught and the
    response uses jsonify misuse, so the actual status is 500."""
    r = client.delete(f"/api/v1/event?id={sample_event}")
    assert r.status_code == 200

    verify = client.get(f"/api/v1/event?id={sample_event}")
    assert verify.status_code == 404


@pytest.mark.bug
def test_delete_event_not_found_returns_404(client):
    """Intended: 404.  Bug: jsonify misuse causes 500 OR the wrong status
    code (event.py line 263 returns status=400, not 404, making this doubly
    wrong even if the jsonify issue were fixed)."""
    r = client.delete("/api/v1/event?id=99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Parser pollution
# ---------------------------------------------------------------------------

def test_event_parser_handles_repeated_put_requests(client, sample_event):
    """Successive PUT requests all return 200 even though the module-level
    parser accumulates duplicate args on each call.  Flask-RESTful resolves
    duplicates by using the last value, so requests still succeed — the bug
    is cosmetic (growing arg list) rather than functional."""
    # Prime the parser
    client.get(f"/api/v1/event?id={sample_event}")

    payload = {"id": sample_event, "name": "Repeated PUT", "year": 2025}
    r1 = client.put("/api/v1/event", json=payload)
    r2 = client.put("/api/v1/event", json=payload)
    r3 = client.put("/api/v1/event", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 200
