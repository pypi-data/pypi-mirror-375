"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from typing import Any

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_checkly.tap import TapCheckly

SAMPLE_CONFIG: dict[str, Any] = {}

TestTapCheckly = get_tap_test_class(
    TapCheckly,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "check_alerts",
            "check_groups",
            "dashboards",
            "maintenance_windows",
            "private_locations",
            "snippets",
        ],
    ),
)
