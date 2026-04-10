"""
Integration tests for /api/v1/household and /api/v1/all_households.

This is the most "correct" resource in the codebase:
  - POST uses Household(**args) properly (not **args.__str__()).
  - DELETE uses db.session.delete() properly.
  - All field assignments in PUT are correct.

The only bugs here are the pervasive jsonify misuse on error paths, which
causes 500 responses instead of the intended 4xx status codes.

Tests marked @pytest.mark.bug document INTENDED behavior.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /api/v1/all_households
# ---------------------------------------------------------------------------

def test_get_all_households_empty_db(client):
    r = client.get("/api/v1/all_households")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_all_households_returns_all_records(client, sample_household):
    r = client.get("/api/v1/all_households")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_all_households_multiple_records(client):
    from models.models import Household
    from backend import db as _db
    for nick in ("Alpha", "Beta", "Gamma"):
        h = Household(nickname=nick)
        _db.session.add(h)
    _db.session.commit()

    r = client.get("/api/v1/all_households")
    assert r.status_code == 200
    assert len(r.get_json()) == 3


def test_get_all_households_contains_expected_fields(client, sample_household):
    data = client.get("/api/v1/all_households").get_json()
    first = data[0]
    for key in ("id", "nickname", "first_names", "surname", "is_relevant",
                "should_receive_holiday_card"):
        assert key in first


# ---------------------------------------------------------------------------
# GET /api/v1/household  (single record)
# ---------------------------------------------------------------------------

def test_get_household_success(client, sample_household):
    r = client.get(f"/api/v1/household?id={sample_household}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == sample_household
    assert data["nickname"] == "TestFamily"
    assert data["first_names"] == "Alice Bob"
    assert data["surname"] == "Smith"


def test_get_household_boolean_fields_are_booleans(client, sample_household):
    data = client.get(f"/api/v1/household?id={sample_household}").get_json()
    assert isinstance(data["is_relevant"], bool)
    assert isinstance(data["should_receive_holiday_card"], bool)


@pytest.mark.bug
def test_get_household_not_found_returns_404(client):
    """Intended: 404 when no household exists for the given id.
    Bug: jsonify misuse causes a 500 response instead."""
    r = client.get("/api/v1/household?id=99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/household
# ---------------------------------------------------------------------------

def test_post_household_creates_record(client):
    """Household POST is the one POST endpoint that works correctly.
    It uses Household(**args) instead of **args.__str__().
    Also creates a blank Address record alongside the new Household."""
    payload = {
        "id": 1,
        "nickname": "NewFamily",
        "first_names": "Carol Dave",
        "surname": "Jones",
    }
    r = client.post("/api/v1/household", json=payload)
    assert r.status_code == 201
    household_id = r.get_json()
    assert isinstance(household_id, int)


def test_post_household_also_creates_blank_address(client):
    """Creating a Household via POST automatically creates a blank Address."""
    from models.models import Address
    from backend import db as _db

    payload = {"id": 1, "nickname": "WithAddress"}
    client.post("/api/v1/household", json=payload)

    addresses = _db.session.execute(
        __import__("sqlalchemy").select(Address)
    ).scalars().all()
    assert len(addresses) == 1


def test_post_household_record_is_retrievable(client):
    payload = {"id": 1, "nickname": "Retrievable", "first_names": "Eve"}
    r = client.post("/api/v1/household", json=payload)
    assert r.status_code == 201
    new_id = r.get_json()

    verify = client.get(f"/api/v1/household?id={new_id}")
    assert verify.status_code == 200
    assert verify.get_json()["nickname"] == "Retrievable"


# ---------------------------------------------------------------------------
# PUT /api/v1/household
# ---------------------------------------------------------------------------

def test_put_household_updates_nickname(client, sample_household):
    payload = {"id": sample_household, "nickname": "RenamedFamily"}
    r = client.put("/api/v1/household", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/household?id={sample_household}")
    assert verify.get_json()["nickname"] == "RenamedFamily"


def test_put_household_updates_relationship(client, sample_household):
    # The PUT route unconditionally writes ALL parsed args back to the record.
    # nickname is NOT NULL in the DB, so we must include it to avoid a
    # constraint error — even though this test is only verifying relationship.
    payload = {"id": sample_household, "nickname": "TestFamily", "relationship": "Colleague"}
    r = client.put("/api/v1/household", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/household?id={sample_household}")
    assert verify.get_json()["relationship"] == "Colleague"


def test_put_household_updates_should_receive_holiday_card(client, sample_household):
    payload = {"id": sample_household, "nickname": "TestFamily",
               "should_receive_holiday_card": "false"}
    r = client.put("/api/v1/household", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/household?id={sample_household}")
    assert verify.get_json()["should_receive_holiday_card"] is False


def test_put_household_returns_household_id(client, sample_household):
    r = client.put("/api/v1/household", json={"id": sample_household, "nickname": "TestFamily"})
    assert r.get_json() == sample_household


@pytest.mark.bug
def test_put_household_not_found_returns_404(client):
    """Intended: 404 when household does not exist.
    Bug: jsonify misuse causes 500 instead."""
    r = client.put("/api/v1/household", json={"id": 99999, "nickname": "Ghost"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/household
# ---------------------------------------------------------------------------

def test_delete_household_success(client, sample_household):
    """Household DELETE correctly uses db.session.delete() — this works."""
    r = client.delete(f"/api/v1/household?id={sample_household}")
    assert r.status_code == 200


def test_delete_household_removes_record_from_db(client, sample_household):
    client.delete(f"/api/v1/household?id={sample_household}")
    verify = client.get(f"/api/v1/household?id={sample_household}")
    # Record should be gone; intended 404 (may be 500 due to jsonify bug)
    assert verify.status_code != 200


@pytest.mark.bug
def test_delete_household_not_found_returns_404(client):
    """Intended: 404 when household does not exist.
    Bug: jsonify misuse causes 500 instead."""
    r = client.delete("/api/v1/household?id=99999")
    assert r.status_code == 404
