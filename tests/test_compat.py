"""Tests for the Home Assistant version shims in compat.py."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("homeassistant")

from custom_components.wattpilot.compat import device_config_entry_ids, vol


def test_device_config_entry_ids_prefers_the_single_config_entry_id():
    """A current device names its one config entry and the deprecated set is never read."""

    class _Device:
        config_entry_id = "entry-1"

        @property
        def config_entries(self):
            raise AssertionError("the deprecated config_entries property was read")

    assert device_config_entry_ids(_Device()) == ("entry-1",)


def test_device_config_entry_ids_falls_back_to_the_config_entries_set():
    """A device from a release before 2026.8 only has the set."""
    device = SimpleNamespace(config_entries={"entry-1"})

    assert device_config_entry_ids(device) == ("entry-1",)


def test_device_config_entry_ids_is_empty_for_a_device_without_entries():
    """An orphaned device on a current release has no config entry id."""
    device = SimpleNamespace(config_entry_id=None, config_entries=set())

    assert device_config_entry_ids(device) == ()


def test_vol_provides_the_names_the_integration_uses():
    """Whichever engine is installed, it offers every schema name the package uses."""
    for name in ("Invalid", "Optional", "Required", "Schema", "UNDEFINED"):
        assert hasattr(vol, name), name
