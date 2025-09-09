"""Better Stack tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_betterstack.streams import uptime


class TapBetterStack(Tap):
    """Singer tap for Better Stack."""

    name = "tap-betterstack"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="API Token for Better Stack",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
        additional_properties=False,
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Better Stack streams.
        """
        return [
            uptime.Monitors(tap=self),
            uptime.MonitorGroups(tap=self),
            uptime.Heartbeats(tap=self),
            uptime.HeartbeatGroups(tap=self),
            uptime.OnCalls(tap=self),
            uptime.EscalationPolicies(tap=self),
            uptime.Incidents(tap=self),
            uptime.IncidentTimelineEvents(tap=self),
            uptime.EmailIntegrations(tap=self),
            uptime.IncomingWebhooks(tap=self),
            uptime.StatusPages(tap=self),
        ]
