"""
Integration tests for /api/v1/address and /api/v1/all_addresses.

Bug notes for this resource:
  - POST:   Address(**args.__str__()) passes a string instead of kwargs to the
            constructor (TypeError), and db.session.add() is never called.
  - DELETE: address_to_delete.delete() is not valid in SQLAlchemy 2.x;
            raises AttributeError, which is caught and treated as not-found.
  - Error returns: jsonify({"error": ...}, status=N) misuses Flask's jsonify
            — the `status` kwarg ends up in the JSON body, not as the HTTP
            status code.  Not-found paths return an error response instead of
            the intended 404.

Tests marked @pytest.mark.bug document INTENDED behavior; they are expected
to fail until the underlying bug is fixed.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /api/v1/all_addresses
# ---------------------------------------------------------------------------

def test_get_all_addresses_empty_db(client):
    r = client.get("/api/v1/all_addresses")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_all_addresses_returns_list(client, sample_address, sample_household):
    r = client.get("/api/v1/all_addresses")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_all_addresses_contains_expected_fields(client, sample_address):
    r = client.get("/api/v1/all_addresses")
    first = r.get_json()[0]
    assert "id" in first
    assert "household_id" in first
    assert "line_1" in first
    assert "city" in first


# ---------------------------------------------------------------------------
# GET /api/v1/address  (single record)
# ---------------------------------------------------------------------------

def test_get_address_success(client, sample_address):
    r = client.get(f"/api/v1/address?id={sample_address}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == sample_address
    assert data["line_1"] == "123 Main St"
    assert data["city"] == "Springfield"


def test_get_address_returns_correct_household_id(client, sample_address, sample_household):
    r = client.get(f"/api/v1/address?id={sample_address}")
    assert r.get_json()["household_id"] == sample_household


def test_get_address_boolean_fields_are_booleans(client, sample_address):
    data = client.get(f"/api/v1/address?id={sample_address}").get_json()
    assert isinstance(data["is_current"], bool)
    assert isinstance(data["is_likely_to_change"], bool)
    assert isinstance(data["mail_the_card_to_this_address"], bool)


@pytest.mark.bug
def test_get_address_not_found_returns_404(client):
    """Intended: 404 when no address exists for the given id.
    Bug: jsonify({"error": ...}, status=404) raises TypeError inside Flask,
    so Flask-RESTful's error handler returns 500 instead."""
    r = client.get("/api/v1/address?id=99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/address
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_post_address_creates_record(client, sample_household):
    """Intended: POST with valid data creates an Address and returns 201.
    Bug 1: Address(**args.__str__()) passes a string to the constructor
           (TypeError) instead of unpacking kwargs.
    Bug 2: db.session.add() is never called, so even a correct constructor
           call would not persist the record."""
    payload = {
        "id": 99,
        "household_id": sample_household,
        "line_1": "789 Elm St",
        "city": "Shelbyville",
        "state": "IL",
        "zip": "62702",
        "country": "United States",
        "is_current": "True",
        "is_likely_to_change": "False",
        "mail_the_card_to_this_address": "True",
    }
    r = client.post("/api/v1/address", json=payload)
    assert r.status_code == 201


# ---------------------------------------------------------------------------
# PUT /api/v1/address
# ---------------------------------------------------------------------------

def test_put_address_updates_line_1(client, sample_address):
    payload = {"id": sample_address, "line_1": "999 New Street"}
    r = client.put("/api/v1/address", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/address?id={sample_address}")
    assert verify.get_json()["line_1"] == "999 New Street"


def test_put_address_updates_city(client, sample_address):
    payload = {"id": sample_address, "city": "Ogdenville"}
    r = client.put("/api/v1/address", json=payload)
    assert r.status_code == 200

    verify = client.get(f"/api/v1/address?id={sample_address}")
    assert verify.get_json()["city"] == "Ogdenville"


def test_put_address_returns_address_id(client, sample_address):
    r = client.put("/api/v1/address", json={"id": sample_address, "city": "North Haverbrook"})
    assert r.get_json() == sample_address


@pytest.mark.bug
def test_put_address_not_found_returns_404(client):
    """Intended: 404 when address does not exist.
    Bug: the error return uses jsonify misuse, yielding 500 instead."""
    r = client.put("/api/v1/address", json={"id": 99999, "city": "Nowhere"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/address
# ---------------------------------------------------------------------------

@pytest.mark.bug
def test_delete_address_success(client, sample_address):
    """Intended: DELETE removes the record and returns 200.
    Bug: address_to_delete.delete() is not a valid SQLAlchemy 2.x method;
    raises AttributeError, which is caught and treated as 'not found'.
    The record is NOT deleted."""
    r = client.delete(f"/api/v1/address?id={sample_address}")
    assert r.status_code == 200

    # After deletion the record should be gone
    verify = client.get(f"/api/v1/address?id={sample_address}")
    assert verify.status_code == 404


@pytest.mark.bug
def test_delete_address_not_found_returns_404(client):
    """Intended: 404 when address does not exist.
    Bug: jsonify misuse means the response is not a true 404."""
    r = client.delete("/api/v1/address?id=99999")
    assert r.status_code == 404
