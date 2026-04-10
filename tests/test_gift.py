"""
Integration tests for /api/v1/gift and /api/v1/all_gifts.

Bug notes for this resource:
  - Parser pollution: same pattern as event.py — 'id' is only added to the
    module-level parser when GET or DELETE is called.  PUT tests prime the
    parser with a GET call first.
  - POST:   Gift(**args.__str__()) passes a string instead of kwargs
            (TypeError); db.session.add() is also missing.
  - PUT:    gift.households = args["households"] raises KeyError because
            'households' is not a parser argument; this makes the entire PUT
            broken regardless of other fields.
  - DELETE: gift_to_delete.delete() is not valid in SQLAlchemy 2.x.
  - Error returns: jsonify misuse causes 500 instead of intended status.

Tests marked @pytest.mark.bug document INTENDED behavior.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /api/v1/all_gifts
# ---------------------------------------------------------------------------

def test_get_all_gifts_empty_db(client):
    r = client.get("/api/v1/all_gifts")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_all_gifts_returns_all_records(client, sample_gift):
    r = client.get("/api/v1/all_gifts")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_get_all_gifts_contains_expected_fields(client, sample_gift):
    first = client.get("/api/v1/all_gifts").get_json()[0]
    for key in ("id", "event_id", "description", "should_a_card_be_sent"):
        assert key in first


# ---------------------------------------------------------------------------
# GET /api/v1/gift  (single record)
# ---------------------------------------------------------------------------

def test_get_gift_success(client, sample_gift):
    r = client.get(f"/api/v1/gift?id={sample_gift}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == sample_gift
    assert data["description"] == "Cashmere sweater"


def test_get_gift_should_a_card_be_sent_is_bool(client, sample_gift):
    data = client.get(f"/api/v1/gift?id={sample_gift}").get_json()
    assert isinstance(data["should_a_card_be_sent"], bool)
    assert data["should_a_card_be_sent"] is True


def test_get_gift_date_as_string(client, sample_gift):
    data = client.get(f"/api/v1/gift?id={sample_gift}").get_json()
    assert data["date"] == "2025-12-25"


@pytest.mark.bug
def test_get_gift_not_found_returns_404(client):
    """Intended: 404.  Bug: jsonify misuse causes 500."""
    r = client.get("/api/v1/gift?id=99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/gift
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_post_gift_creates_record(client, sample_event, sample_household):
    """Intended: POST with valid data creates a Gift and returns 201.
    Bug 1: Gift(**args.__str__()) passes a string to the constructor.
    Bug 2: db.session.add() is never called."""
    payload = {
        "event_id": sample_event,
        "household_id": sample_household,
        "description": "New gift",
        "type": "Toy",
        "origin": "Store",
        "date": "2025-12-25",
        "should_a_card_be_sent": "True",
    }
    r = client.post("/api/v1/gift", json=payload)
    assert r.status_code == 201


# ---------------------------------------------------------------------------
# PUT /api/v1/gift
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_put_gift_updates_description(client, sample_gift):
    """Intended: PUT with a new description updates the record and returns 200.
    Bug: args["households"] raises KeyError before any field is written,
    so PUT always returns 500."""
    # Prime the parser
    client.get(f"/api/v1/gift?id={sample_gift}")

    payload = {"id": sample_gift, "description": "Updated description"}
    r = client.put("/api/v1/gift", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/gift?id={sample_gift}")
    assert verify.get_json()["description"] == "Updated description"


@pytest.mark.bug
def test_put_gift_updates_origin(client, sample_gift):
    """Intended: PUT updates the origin field.
    Additional bug (beyond KeyError): even if the KeyError were fixed,
    gift.origin is assigned twice (once from args['type'], once from
    args['origin']), overwriting the first assignment."""
    client.get(f"/api/v1/gift?id={sample_gift}")

    payload = {"id": sample_gift, "origin": "Online"}
    r = client.put("/api/v1/gift", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/gift?id={sample_gift}")
    assert verify.get_json()["origin"] == "Online"


@pytest.mark.bug
def test_put_gift_updates_date(client, sample_gift):
    """Intended: PUT updates the date field.
    Additional bug: gift.date is assigned from args['should_a_card_be_sent']
    instead of args['date']."""
    client.get(f"/api/v1/gift?id={sample_gift}")

    payload = {"id": sample_gift, "date": "2026-01-15"}
    r = client.put("/api/v1/gift", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/gift?id={sample_gift}")
    assert verify.get_json()["date"] == "2026-01-15"


@pytest.mark.bug
def test_put_gift_not_found_returns_404(client):
    """Intended: 404.  Bug: KeyError crashes before the DB query even runs."""
    client.get("/api/v1/gift?id=99999")
    r = client.put("/api/v1/gift", json={"id": 99999, "description": "Ghost"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/gift
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_delete_gift_success(client, sample_gift):
    """Intended: DELETE removes the record and returns 200.
    Bug: gift_to_delete.delete() is not a valid SQLAlchemy 2.x method."""
    r = client.delete(f"/api/v1/gift?id={sample_gift}")
    assert r.status_code == 200

    verify = client.get(f"/api/v1/gift?id={sample_gift}")
    assert verify.status_code == 404


@pytest.mark.bug
def test_delete_gift_not_found_returns_404(client):
    """Intended: 404.  Bug: jsonify misuse causes 500."""
    r = client.delete("/api/v1/gift?id=99999")
    assert r.status_code == 404
