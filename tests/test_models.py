"""
Unit tests for models/models.py.

These tests exercise model construction, to_dict(), field defaults, and
database constraints directly via SQLAlchemy — no HTTP requests involved.
All tests here are expected to pass.
"""

import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from backend import db as _db
from models.models import Address, Household, Event, Gift, Card, Picklists


# ---------------------------------------------------------------------------
# Household
# ---------------------------------------------------------------------------

def test_household_to_dict_has_expected_keys(sample_household):
    hh = _db.session.get(Household, sample_household)
    d = hh.to_dict()
    expected = {
        "id", "nickname", "first_names", "surname", "address_to",
        "formal_name", "known_from", "relationship", "relationship_type",
        "family_side", "kids", "pets", "should_receive_holiday_card",
        "is_relevant", "created_date", "last_modified", "notes",
    }
    assert expected.issubset(d.keys())


def test_household_to_dict_values_match(sample_household):
    hh = _db.session.get(Household, sample_household)
    d = hh.to_dict()
    assert d["nickname"] == "TestFamily"
    assert d["first_names"] == "Alice Bob"
    assert d["surname"] == "Smith"


def test_household_nickname_unique_constraint(sample_household):
    duplicate = Household(nickname="TestFamily")
    _db.session.add(duplicate)
    with pytest.raises(IntegrityError):
        _db.session.commit()
    _db.session.rollback()


def test_household_is_relevant_default():
    h = Household(nickname="DefaultTest")
    _db.session.add(h)
    _db.session.commit()
    assert h.is_relevant == "True"


def test_household_created_date_auto_populated(sample_household):
    hh = _db.session.get(Household, sample_household)
    assert hh.created_date is not None


def test_household_last_modified_auto_populated(sample_household):
    hh = _db.session.get(Household, sample_household)
    assert hh.last_modified is not None


def test_household_repr_is_string(sample_household):
    hh = _db.session.get(Household, sample_household)
    assert isinstance(repr(hh), str)
    assert len(repr(hh)) > 0


# ---------------------------------------------------------------------------
# Address
# ---------------------------------------------------------------------------

def test_address_to_dict_has_expected_keys(sample_address):
    addr = _db.session.get(Address, sample_address)
    d = addr.to_dict()
    expected = {
        "id", "household_id", "line_1", "line_2", "city", "state", "zip",
        "country", "full_address", "is_current", "is_likely_to_change",
        "mail_the_card_to_this_address", "created_date", "last_modified", "notes",
    }
    assert expected.issubset(d.keys())


def test_address_boolean_fields_convert_to_bool_in_to_dict(sample_address):
    addr = _db.session.get(Address, sample_address)
    d = addr.to_dict()
    assert isinstance(d["is_current"], bool)
    assert isinstance(d["is_likely_to_change"], bool)
    assert isinstance(d["mail_the_card_to_this_address"], bool)


def test_address_is_current_true(sample_address):
    addr = _db.session.get(Address, sample_address)
    assert addr.to_dict()["is_current"] is True


def test_address_is_likely_to_change_false(sample_address):
    addr = _db.session.get(Address, sample_address)
    assert addr.to_dict()["is_likely_to_change"] is False


def test_address_country_default():
    # Create address without specifying country; default should be "United States"
    a = Address(line_1="456 Oak Ave", is_current="True",
                is_likely_to_change="False", mail_the_card_to_this_address="True")
    _db.session.add(a)
    _db.session.commit()
    assert a.country == "United States"


def test_address_created_date_auto_populated(sample_address):
    addr = _db.session.get(Address, sample_address)
    assert addr.created_date is not None


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------

def test_event_to_dict_has_expected_keys(sample_event):
    e = _db.session.get(Event, sample_event)
    d = e.to_dict()
    assert {"id", "name", "date", "year", "is_archived", "notes"}.issubset(d.keys())


def test_event_to_dict_date_as_string(sample_event):
    e = _db.session.get(Event, sample_event)
    d = e.to_dict()
    assert d["date"] == "2025-12-25"


def test_event_is_archived_bool_in_to_dict(sample_event):
    e = _db.session.get(Event, sample_event)
    assert isinstance(e.to_dict()["is_archived"], bool)
    assert e.to_dict()["is_archived"] is False


def test_event_year_defaults_to_current_year():
    e = Event(name="No Year Event")
    _db.session.add(e)
    _db.session.commit()
    assert e.year == datetime.now().year


def test_event_repr_is_string(sample_event):
    e = _db.session.get(Event, sample_event)
    assert isinstance(repr(e), str)


# ---------------------------------------------------------------------------
# Gift
# ---------------------------------------------------------------------------

def test_gift_to_dict_has_expected_keys(sample_gift):
    g = _db.session.get(Gift, sample_gift)
    d = g.to_dict()
    assert {"id", "event_id", "description", "type", "origin",
            "date", "should_a_card_be_sent", "notes"}.issubset(d.keys())


def test_gift_should_a_card_be_sent_bool_in_to_dict(sample_gift):
    g = _db.session.get(Gift, sample_gift)
    assert isinstance(g.to_dict()["should_a_card_be_sent"], bool)
    assert g.to_dict()["should_a_card_be_sent"] is True


def test_gift_date_as_string_in_to_dict(sample_gift):
    g = _db.session.get(Gift, sample_gift)
    assert g.to_dict()["date"] == "2025-12-25"


def test_gift_repr_is_string(sample_gift):
    g = _db.session.get(Gift, sample_gift)
    assert isinstance(repr(g), str)


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

def test_card_to_dict_has_expected_keys(sample_card):
    c = _db.session.get(Card, sample_card)
    d = c.to_dict()
    assert {"id", "type", "was_returned", "gift_id", "event_id",
            "household_id", "address_id", "date_sent", "notes"}.issubset(d.keys())


def test_card_date_sent_as_string_in_to_dict(sample_card):
    c = _db.session.get(Card, sample_card)
    assert c.to_dict()["date_sent"] == "2025-12-26"


def test_card_date_sent_none_when_not_set():
    c = Card(type="Holiday")
    _db.session.add(c)
    _db.session.commit()
    assert c.to_dict()["date_sent"] is None


def test_card_repr_is_string(sample_card):
    c = _db.session.get(Card, sample_card)
    assert isinstance(repr(c), str)


# ---------------------------------------------------------------------------
# Picklists
# ---------------------------------------------------------------------------

def test_picklists_to_dict_splits_comma_separated_values(sample_picklist):
    p = _db.session.get(Picklists, sample_picklist)
    d = p.to_dict()
    assert d["household_relationship"] == ["Friend", "Family", "Colleague"]
    assert d["household_relationship_type"] == ["Close", "Casual"]
    assert d["household_family_side"] == ["Mine", "Partner"]
    assert d["card_type"] == ["Holiday", "Thank You", "Birthday"]


def test_picklists_to_dict_has_expected_keys(sample_picklist):
    p = _db.session.get(Picklists, sample_picklist)
    d = p.to_dict()
    assert {"version", "household_relationship", "household_relationship_type",
            "household_family_side", "card_type"}.issubset(d.keys())


def test_picklists_repr_is_string(sample_picklist):
    p = _db.session.get(Picklists, sample_picklist)
    assert isinstance(repr(p), str)
