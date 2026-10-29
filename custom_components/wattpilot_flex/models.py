"""Typed entry data, runtime data and catalog definitions for the Fronius Wattpilot integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from collections.abc import Callable

    from wattpilot_api import Wattpilot

# Where an entity reads its value. "none" is what the button platform forces:
# a button has no state to read.
type EntitySource = Literal["attribute", "namespacelist", "none", "property"]


class WattpilotEntryData(TypedDict, total=False):
    """The connection details a config entry stores in ``entry.data``.

    Every field is optional. ``connection`` is missing on entries created before
    the cloud option, which were all local. ``serial`` is missing on a local
    entry whose charger reports none, and ``ip_address`` on a cloud entry. Each
    reader supplies its own default, ``DEFAULT_TIMEOUT`` for ``timeout``.
    """

    connection: Literal["cloud", "local"]
    friendly_name: str
    ip_address: str
    password: str
    serial: str
    timeout: int


def entry_config(entry: ConfigEntry[Any]) -> WattpilotEntryData:
    """Return a config entry's data, typed as the connection details it stores.

    Home Assistant types ``entry.data`` as ``MappingProxyType[str, Any]``, and this
    is the one place the integration narrows it. The cast does not check anything
    at runtime, and the mapping stays read-only: change an entry through
    ``async_update_entry`` or ``async_update_reload_and_abort``, never in place.

    Args:
        entry: A config entry of this integration.

    Returns:
        The entry's data.
    """
    return cast("WattpilotEntryData", entry.data)


class EntityDefinition(TypedDict, total=False):
    """One entity definition from a platform's YAML catalog.

    The header comment of ``sensor.yaml`` documents what each field does. Every
    field is optional here: ``catalog.py`` checks the ones a platform requires
    (``id`` and ``source`` by default) before it builds the entity. The catalogs
    are parsed YAML, so nothing enforces these types at runtime;
    ``tests/test_yaml_catalogs.py`` rejects a catalog key that is not declared here.
    """

    attribute_ids: list[str]
    attribute_props: dict[str, str]
    connection: str
    default_state: str | int | float
    description: str
    device_class: str
    enabled: bool
    entity_category: str
    enum: dict[int, str]
    factor: float
    firmware: str
    html_unescape: bool
    id: str
    id_installed: str
    id_status: str
    id_trigger: str
    invert: bool
    mode: str
    name: str
    namespace_id: int
    native_max_value: float
    native_min_value: float
    native_step: float
    options: dict[int | str, str] | str
    options_property: str
    schedule: bool
    set_type: str
    set_value: str | int | float | bool
    source: EntitySource
    state_class: str
    suggested_unit_of_measurement: str
    uid: str
    unit_of_measurement: str
    value_id: int | str
    value_props: dict[int, str]
    value_reduce: str
    variant: int | str


@dataclass
class WattpilotRuntimeData:
    """What a loaded config entry keeps on ``entry.runtime_data``.

    Attributes:
        charger: The connected ``Wattpilot`` client.
        params: The entry's connection details, as they were when it was set up.
        debug_properties: Property-change debug logging: ``True`` for every
            property, a list for only those, ``False`` for none. Set by the
            ``set_debug_properties`` action.
        property_updates_unsub: Unsubscribes the property-change callback.
        connection_monitor_cancel: Stops the connection monitor's timer.
        cloud_api_key: The go-e cloud API key the charger returned, ``False``
            once the cloud API was disabled or no key arrived. Set by the
            ``set_goe_cloud`` action.
        cloud_api_url: The go-e cloud API URL for this charger, set alongside
            ``cloud_api_key``.
    """

    charger: Wattpilot
    params: WattpilotEntryData
    debug_properties: bool | list[str] = False
    property_updates_unsub: Callable[[], None] | None = None
    connection_monitor_cancel: Callable[[], None] | None = None
    cloud_api_key: str | Literal[False] | None = None
    cloud_api_url: str | None = None


type WattpilotConfigEntry = ConfigEntry[WattpilotRuntimeData]
