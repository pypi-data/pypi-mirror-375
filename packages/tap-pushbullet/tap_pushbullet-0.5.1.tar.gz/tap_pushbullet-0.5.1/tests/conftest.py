"""Pytest configuration."""

from __future__ import annotations

import fnmatch

import pytest

XFAIL_NULLABLE = pytest.mark.xfail(reason="Null not documented in OpenAPI spec")
XFAIL_SCHEMA_MISMATCH = pytest.mark.xfail(reason="Schema mismatch against OpenAPI spec")
XFAIL_NO_RECORDS = pytest.mark.xfail(reason="No records returned from API")

SCHEMA_MISMATCH = {
    "test_tap_stream_transformed_catalog_schema_matches_record[chats]",
}
NULLABLE: set[str] = set()
NO_RECORDS = {
    "test_tap_stream_returns_record[[]chats[]]",
    "test_tap_stream_attribute_is_boolean[[]chats.*[]]",
    "test_tap_stream_attribute_is_numeric[[]chats.*[]]",
    "test_tap_stream_attribute_is_object[[]chats.*[]]",
}


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Skip tests that require a live API key."""
    test_name = item.name.split("::")[-1]

    if any(fnmatch.fnmatch(test_name, pattern) for pattern in NULLABLE):
        item.add_marker(XFAIL_NULLABLE)

    if any(fnmatch.fnmatch(test_name, pattern) for pattern in SCHEMA_MISMATCH):
        item.add_marker(XFAIL_SCHEMA_MISMATCH)

    if any(fnmatch.fnmatch(test_name, pattern) for pattern in NO_RECORDS):
        item.add_marker(XFAIL_NO_RECORDS)
