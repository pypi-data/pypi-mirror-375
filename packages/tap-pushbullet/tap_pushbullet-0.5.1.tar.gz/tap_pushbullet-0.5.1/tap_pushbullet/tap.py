"""Pushbullet tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_pushbullet import streams


class TapPushbullet(Tap):
    """Singer tap for Pushbullet."""

    name = "tap-pushbullet"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="API Key for Pushbullet",
        ),
        th.Property(
            "start_date",
            th.NumberType,
            description="Earliest Unix timestamp to get data from",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Pushbullet streams.
        """
        return [
            streams.Chats(tap=self),
            streams.Devices(tap=self),
            streams.Pushes(tap=self),
            streams.Subscriptions(tap=self),
        ]
