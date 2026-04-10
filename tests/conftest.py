"""
Shared fixtures for all greeting-cards backend tests.

Test strategy:
- SQLite in-memory database replaces PostgreSQL; no external DB required.
- The Flask app and all routes are created once per session (session-scoped `app`).
- The database is wiped between each test via the autouse `clean_db` fixture.
- Tests for INTENDED behavior that currently fail due to bugs are marked @pytest.mark.bug.
"""

import pytest
from datetime import date
from flask_restful import Api

from backend import create_app, db as _db

# ---------------------------------------------------------------------------
# Flask 3.x / Werkzeug 3.x compatibility patch
#
# Flask-RESTful's reqparse calls getattr(request, 'json', None) to probe
# whether a JSON body is present.  In Werkzeug 3.x, request.json is a
# property that raises UnsupportedMediaType (415) when Content-Type is not
# application/json.  getattr only suppresses AttributeError, so the
# exception escapes and every GET/DELETE with a query-string id returns 415.
#
# Fix: wrap the property so it returns None instead of raising for
# non-JSON requests.  This is applied once at import time.
# ---------------------------------------------------------------------------
from werkzeug.wrappers import Request as _WerkzeugRequest

_orig_json_fget = _WerkzeugRequest.json.fget


def _safe_json(self):  # noqa: D401
    try:
        return _orig_json_fget(self)
    except Exception:
        return None


_WerkzeugRequest.json = property(_safe_json)  # type: ignore[assignment]
from models.models import Address, Household, Event, Gift, Card, Picklists
from routes.address import AddressApi, AddressCollectionApi
from routes.household import HouseholdApi, HouseholdCollectionApi
from routes.event import EventApi, EventCollectionApi
from routes.gift import GiftApi, GiftCollectionApi
from routes.card import CardApi, CardCollectionApi
from routes.picklists import PicklistValuesApi


class TestConfig:
    """Minimal Flask config for the test suite.  Overrides the real Config class."""
    TESTING = True
    DEBUG = False
    # Prevent Flask from re-raising exceptions that occur inside route handlers.
    # TESTING=True normally sets propagation to True, which means the jsonify
    # misuse bug (TypeError) in several routes would propagate to the test client
    # instead of being caught by Flask's error handler and returned as a 500.
    # Setting this explicitly False lets the 500 response reach the test.
    PROPAGATE_EXCEPTIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"check_same_thread": False}}
    SECRET_KEY = "test-secret-key"
    DEBUG_ENABLED = False
    CORS_HEADERS = "Content-Type"
    WHITELISTED_ORIGINS = ""


@pytest.fixture(scope="session")
def app():
    """Create the Flask app once for the entire test session.

    Routes are registered here, mirroring what main.py does.  This must be
    session-scoped because Flask-RESTful raises an error if routes are
    registered more than once on the same app.
    """
    application = create_app(TestConfig)

    api = Api(application)
    api.add_resource(AddressApi, "/api/v1/address")
    api.add_resource(AddressCollectionApi, "/api/v1/all_addresses")
    api.add_resource(HouseholdApi, "/api/v1/household")
    api.add_resource(HouseholdCollectionApi, "/api/v1/all_households")
    api.add_resource(EventApi, "/api/v1/event")
    api.add_resource(EventCollectionApi, "/api/v1/all_events")
    api.add_resource(GiftApi, "/api/v1/gift")
    api.add_resource(GiftCollectionApi, "/api/v1/all_gifts")
    api.add_resource(CardApi, "/api/v1/card")
    api.add_resource(CardCollectionApi, "/api/v1/all_cards")
    api.add_resource(PicklistValuesApi, "/api/v1/picklist_values")

    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    """Return a Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Wipe all table rows after each test.

    Runs automatically for every test (autouse=True).  Depends on `app` so
    that the session-scoped app fixture (and its app_context) is always
    initialized before any test body runs.

    NOTE: SQLite does not enforce foreign keys by default, so we can delete
    in any order.  Reversed metadata order is used anyway to be safe.
    """
    yield
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()
    # Evict all ORM objects from the identity map so the next test's fixtures
    # don't collide when SQLite reuses the same primary key (SQLite resets its
    # rowid counter to 1 after all rows are deleted from a table, unlike
    # PostgreSQL sequences which keep incrementing).
    _db.session.expunge_all()


# ---------------------------------------------------------------------------
# Seed data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_household():
    """Insert a Household row and return its generated id."""
    h = Household(
        nickname="TestFamily",
        first_names="Alice Bob",
        surname="Smith",
        address_to="The Smiths",
        formal_name="Mr. and Mrs. Smith",
        known_from="School",
        relationship="Friend",
        relationship_type="Close",
        family_side="Mine",
        kids="Emma",
        pets="Fido",
        should_receive_holiday_card=True,
        is_relevant=True,
    )
    _db.session.add(h)
    _db.session.commit()
    return h.id


@pytest.fixture
def sample_address(sample_household):
    """Insert an Address row linked to sample_household; return its id."""
    a = Address(
        household_id=sample_household,
        line_1="123 Main St",
        city="Springfield",
        state="IL",
        zip="62701",
        country="United States",
        is_current="True",
        is_likely_to_change="False",
        mail_the_card_to_this_address="True",
    )
    _db.session.add(a)
    _db.session.commit()
    return a.id


@pytest.fixture
def sample_event():
    """Insert an Event row and return its id."""
    e = Event(
        name="Christmas 2025",
        date=date(2025, 12, 25),
        year=2025,
        is_archived="False",
    )
    _db.session.add(e)
    _db.session.commit()
    return e.id


@pytest.fixture
def sample_gift(sample_household, sample_event):
    """Insert a Gift row and return its id."""
    g = Gift(
        event_id=sample_event,
        household_id=sample_household,
        description="Cashmere sweater",
        type="Clothing",
        origin="Department store",
        date=date(2025, 12, 25),
        should_a_card_be_sent="True",
    )
    _db.session.add(g)
    _db.session.commit()
    return g.id


@pytest.fixture
def sample_card(sample_household, sample_event, sample_gift, sample_address):
    """Insert a Card row and return its id."""
    c = Card(
        type="Thank You",
        was_returned=False,
        gift_id=sample_gift,
        event_id=sample_event,
        household_id=sample_household,
        address_id=sample_address,
        date_sent=date(2025, 12, 26),
    )
    _db.session.add(c)
    _db.session.commit()
    return c.id


@pytest.fixture
def sample_picklist():
    """Insert a Picklists row (version=1) and return its version.

    NOTE: Picklists.__init__ references self.is_default which is not a
    declared SQLAlchemy column.  SQLAlchemy 2.x rejects unknown kwargs, so
    Picklists(is_default=...) raises TypeError before the row is inserted.
    Bypass the ORM constructor entirely with a Core-level INSERT statement.
    """
    from sqlalchemy import insert as _sa_insert
    _db.session.execute(
        _sa_insert(Picklists.__table__).values(
            version=1,
            household_relationship="Friend,Family,Colleague",
            household_relationship_type="Close,Casual",
            household_family_side="Mine,Partner",
            card_type="Holiday,Thank You,Birthday",
        )
    )
    _db.session.commit()
    return 1
