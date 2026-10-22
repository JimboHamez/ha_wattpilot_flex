"""Compatibility with the range of Home Assistant releases the integration supports.

``hacs.json`` declares Home Assistant 2024.11 as the minimum, while the current
release has replaced or deprecated APIs the integration uses. Each shim here
prefers the current API and falls back to the older one, so the rest of the
package can use one name for both.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Home Assistant 2026.9 validates with Probatio and only aliases ``voluptuous``
# to it, and its type hints expect Probatio schemas. Probatio provides every
# name the integration uses (Schema, Required, Optional, Invalid, UNDEFINED).
try:
    import probatio as vol
except ImportError:  # Home Assistant before 2026.9 validates with voluptuous.
    import voluptuous as vol  # type: ignore[no-redef]

if TYPE_CHECKING:
    # Type checking runs against the current release only, where a registry
    # lookup returns a DeviceEntry or a ChildDeviceEntry and both derive from this.
    from homeassistant.helpers.device_registry import BaseDeviceEntry

__all__ = ["device_config_entry_ids", "vol"]


def device_config_entry_ids(device: BaseDeviceEntry) -> tuple[str, ...]:
    """Return the ids of the config entries a device belongs to.

    Home Assistant 2026.8 gave each device a single ``config_entry_id`` and
    deprecated the ``config_entries`` set, which current releases log a warning
    for on every read and which stops working in 2027.10. Older releases only
    have the set.

    Args:
        device: A device registry entry.

    Returns:
        The config entry ids, as a tuple with one id on current releases.
    """
    entry_id: str | None = getattr(device, "config_entry_id", None)
    if entry_id is not None:
        return (entry_id,)
    return tuple(getattr(device, "config_entries", ()))
