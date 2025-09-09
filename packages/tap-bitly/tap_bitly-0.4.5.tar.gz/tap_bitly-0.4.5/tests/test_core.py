"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_bitly.tap import TapBitly

TestTapBitly = get_tap_test_class(
    TapBitly,
    config={},
    suite_config=SuiteConfig(
        max_records_limit=50,
        ignore_no_records_for_streams=[
            "bsds",
            "campaigns",
            "channels",
        ],
    ),
)
