"""
Unit tests for helpers/helpers.py.

These tests have no Flask or database dependencies — they call Python
functions directly.  All tests in this file are expected to pass.
"""

import pytest
from helpers.helpers import (
    convert_to_bool,
    remove_milliseconds_from_datetime_string,
    scrub_password_from_database_uri,
)


# ---------------------------------------------------------------------------
# convert_to_bool
# ---------------------------------------------------------------------------

def test_convert_to_bool_true_boolean():
    assert convert_to_bool(True) is True


def test_convert_to_bool_false_boolean():
    assert convert_to_bool(False) is False


@pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "t", "T", "y", "Y", "yes", "Yes", "YES"])
def test_convert_to_bool_truthy_strings(value):
    assert convert_to_bool(value) is True


@pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "n", "no", "No", "nope", "random"])
def test_convert_to_bool_falsy_strings(value):
    assert convert_to_bool(value) is False


def test_convert_to_bool_int_one():
    assert convert_to_bool(1) is True


def test_convert_to_bool_int_zero():
    assert convert_to_bool(0) is False


def test_convert_to_bool_other_int_returns_false():
    # Any int other than 1 returns False per the implementation
    assert convert_to_bool(42) is False
    assert convert_to_bool(-1) is False


def test_convert_to_bool_unsupported_type_returns_false():
    # Unsupported types (None, list, etc.) fall through to False
    assert convert_to_bool(None) is False
    assert convert_to_bool([]) is False
    assert convert_to_bool({}) is False


# ---------------------------------------------------------------------------
# remove_milliseconds_from_datetime_string
# ---------------------------------------------------------------------------

def test_remove_milliseconds_basic():
    result = remove_milliseconds_from_datetime_string("2025-12-25 10:30:00.123456")
    assert result == "2025-12-25 10:30:00"


def test_remove_milliseconds_no_milliseconds():
    text = "2025-12-25 10:30:00"
    assert remove_milliseconds_from_datetime_string(text) == text


def test_remove_milliseconds_short_fraction():
    result = remove_milliseconds_from_datetime_string("2025-12-25 10:30:00.1")
    assert result == "2025-12-25 10:30:00"


def test_remove_milliseconds_raises_for_int():
    with pytest.raises(TypeError):
        remove_milliseconds_from_datetime_string(20251225)


def test_remove_milliseconds_raises_for_none():
    with pytest.raises(TypeError):
        remove_milliseconds_from_datetime_string(None)


def test_remove_milliseconds_raises_for_list():
    with pytest.raises(TypeError):
        remove_milliseconds_from_datetime_string(["2025-12-25"])


# ---------------------------------------------------------------------------
# scrub_password_from_database_uri
# ---------------------------------------------------------------------------

def test_scrub_password_basic():
    uri = "postgresql+psycopg://myuser:supersecret@192.168.1.1:5432/mydb"
    result = scrub_password_from_database_uri(uri)
    assert "supersecret" not in result
    assert "myuser" in result
    assert "DB_PW" in result


def test_scrub_password_replaces_with_placeholder():
    uri = "postgresql+psycopg://prod:HPpREqN14wk4SSYccpfP@192.168.1.92:15432/cards"
    result = scrub_password_from_database_uri(uri)
    assert result == "postgresql+psycopg://prod:DB_PW@192.168.1.92:15432/cards"


def test_scrub_password_long_password():
    uri = "postgresql+psycopg://dev:9wJ44arq9V5IDbAsuWLiZapzoj0EnE2M6ylH@192.168.1.92:15432/cards-dev"
    result = scrub_password_from_database_uri(uri)
    assert "9wJ44arq9V5IDbAsuWLiZapzoj0EnE2M6ylH" not in result
    assert "DB_PW" in result


def test_scrub_password_no_match_returns_original():
    # A URI that doesn't match the postgresql+psycopg scheme is returned unchanged
    uri = "sqlite:///mydb.sqlite"
    result = scrub_password_from_database_uri(uri)
    assert result == uri
