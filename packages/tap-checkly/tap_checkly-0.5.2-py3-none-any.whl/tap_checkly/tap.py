"""Checkly tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_checkly import streams


class TapCheckly(Tap):
    """Singer tap for Checkly."""

    name = "tap-checkly"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "account_id",
            th.StringType,
            required=True,
            description="Checkly Account ID",
        ),
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="API Token for Checkly",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
        th.Property(
            "include_paid_streams",
            th.BooleanType,
            default=False,
            description="Include streams that require a paid Checkly plan",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Checkly streams.
        """
        included_streams: list[Stream] = [
            streams.AlertChannels(tap=self),
            streams.Checks(tap=self),
            streams.CheckAlerts(tap=self),
            streams.CheckGroups(tap=self),
            streams.Dashboards(tap=self),
            streams.EnvironmentVariables(tap=self),
            streams.Locations(tap=self),
            streams.MaintenanceWindows(tap=self),
            streams.PrivateLocations(tap=self),
            streams.Runtimes(tap=self),
            streams.Snippets(tap=self),
        ]

        if self.config.get("include_paid_streams", False):
            included_streams += [
                streams.AlertNotifications(tap=self),
                streams.CheckResults(tap=self),
            ]

        return included_streams
