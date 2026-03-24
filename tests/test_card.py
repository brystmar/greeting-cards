"""
Integration tests for /api/v1/card and /api/v1/all_cards.

Bug notes for this resource:
  - Parser pollution: same pattern as event.py / gift.py — 'id' is only added
    to the module-level parser when GET or DELETE is called.
  - POST:   Card(**args.__str__()) passes a string instead of kwargs; also
            db.session.add() is missing; and card.status is accessed but the
            Card model has no 'status' column.
  - PUT:    card.households = args["households"] raises KeyError (no such
            parser arg); card.status = args["status"] references a non-existent
            model column; card.date_sent = args["notes"] overwrites date_sent
            with the wrong field.
  - DELETE: card_to_delete.delete() is not valid in SQLAlchemy 2.x.
  - Error returns: jsonify misuse causes 500 instead of intended status.

The Card.GET endpoint itself works correctly — Card.to_dict() does not
reference card.status, so GET reads and returns card data without error.

Tests marked @pytest.mark.bug document INTENDED behavior.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /api/v1/all_cards
# ---------------------------------------------------------------------------

def test_get_all_cards_empty_db(client):
    r = client.get("/api/v1/all_cards")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_all_cards_returns_all_records(client, sample_card):
    r = client.get("/api/v1/all_cards")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_get_all_cards_contains_expected_fields(client, sample_card):
    first = client.get("/api/v1/all_cards").get_json()[0]
    for key in ("id", "type", "was_returned", "gift_id", "event_id",
                "household_id", "address_id", "date_sent"):
        assert key in first


# ---------------------------------------------------------------------------
# GET /api/v1/card  (single record)
# ---------------------------------------------------------------------------

def test_get_card_success(client, sample_card):
    """Card.to_dict() does NOT reference card.status, so GET works correctly."""
    r = client.get(f"/api/v1/card?id={sample_card}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == sample_card
    assert data["type"] == "Thank You"
    assert data["date_sent"] == "2025-12-26"


def test_get_card_returns_all_foreign_keys(client, sample_card, sample_gift,
                                           sample_event, sample_household, sample_address):
    data = client.get(f"/api/v1/card?id={sample_card}").get_json()
    assert data["gift_id"] == sample_gift
    assert data["event_id"] == sample_event
    assert data["household_id"] == sample_household
    assert data["address_id"] == sample_address


@pytest.mark.bug
def test_get_card_not_found_returns_404(client):
    """Intended: 404 when card does not exist.  Bug: jsonify misuse → 500."""
    r = client.get("/api/v1/card?id=99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/card
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_post_card_creates_record(client, sample_event, sample_household,
                                   sample_gift, sample_address):
    """Intended: POST with valid data creates a Card and returns 201.
    Bug 1: Card(**args.__str__()) passes a string to the constructor.
    Bug 2: db.session.add() is never called.
    Bug 3: After construction, card.status is accessed on a model that has no
           'status' column (AttributeError or silent None)."""
    payload = {
        "type": "Holiday",
        "status": "New",
        "event_id": sample_event,
        "household_id": sample_household,
        "gift_id": sample_gift,
        "address_id": sample_address,
    }
    r = client.post("/api/v1/card", json=payload)
    assert r.status_code == 201


# ---------------------------------------------------------------------------
# PUT /api/v1/card
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_put_card_updates_type(client, sample_card):
    """Intended: PUT updates the card type and returns 200.
    Bug: card.households = args["households"] raises KeyError before any field
    is written, so PUT always fails."""
    # Prime the parser
    client.get(f"/api/v1/card?id={sample_card}")

    payload = {"id": sample_card, "type": "Holiday", "status": "New"}
    r = client.put("/api/v1/card", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/card?id={sample_card}")
    assert verify.get_json()["type"] == "Holiday"


@pytest.mark.bug
def test_put_card_updates_date_sent(client, sample_card):
    """Intended: PUT updates date_sent.
    Additional bug (beyond KeyError): card.date_sent = args["notes"], so even
    if the KeyError were fixed, date_sent would be overwritten with the notes
    value."""
    client.get(f"/api/v1/card?id={sample_card}")

    payload = {"id": sample_card, "date_sent": "2026-01-01", "status": "Sent"}
    r = client.put("/api/v1/card", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/card?id={sample_card}")
    assert verify.get_json()["date_sent"] == "2026-01-01"


@pytest.mark.bug
def test_put_card_not_found_returns_404(client):
    """Intended: 404.  Bug: KeyError crashes before DB query."""
    client.get("/api/v1/card?id=99999")
    r = client.put("/api/v1/card", json={"id": 99999, "type": "Holiday", "status": "New"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/card
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_delete_card_success(client, sample_card):
    """Intended: DELETE removes the record and returns 200.
    Bug: card_to_delete.delete() is not a valid SQLAlchemy 2.x method."""
    r = client.delete(f"/api/v1/card?id={sample_card}")
    assert r.status_code == 200

    verify = client.get(f"/api/v1/card?id={sample_card}")
    assert verify.status_code == 404


@pytest.mark.bug
def test_delete_card_not_found_returns_404(client):
    """Intended: 404.  Bug: jsonify misuse causes 500."""
    r = client.delete("/api/v1/card?id=99999")
    assert r.status_code == 404
