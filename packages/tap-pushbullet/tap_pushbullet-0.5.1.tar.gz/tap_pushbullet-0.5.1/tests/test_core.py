"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from typing import Any

from singer_sdk.testing import get_tap_test_class
from tap_pushbullet.tap import TapPushbullet

SAMPLE_CONFIG: dict[str, Any] = {}


TestTapPushbullet = get_tap_test_class(TapPushbullet, config=SAMPLE_CONFIG)
