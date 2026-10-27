"""Validate the data-driven entity YAML catalogs.

Entities in this integration are declared in per-platform YAML files rather
than in Python (see CLAUDE.md -> "Data-driven entities"). These tests guard the
structural contract every entity definition must satisfy, so a malformed
catalog fails here rather than silently dropping entities at runtime.

Pure ``pyyaml`` — no Home Assistant import — so they run without the HA stack.
"""

from __future__ import annotations

import ast
import glob
import os
import re

import pytest
import yaml

from .conftest import COMPONENT_DIR

# Platforms whose YAML top-level key must match the file name.
PLATFORMS = ["sensor", "switch", "select", "number", "button", "update"]
VALID_SOURCES = {"property", "attribute", "namespacelist"}


def _load(platform: str) -> list[dict]:
    path = os.path.join(COMPONENT_DIR, f"{platform}.yaml")
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert platform in data, f"{platform}.yaml missing top-level '{platform}' key"
    return data[platform] or []


def test_all_platform_yaml_files_exist():
    for platform in PLATFORMS:
        assert os.path.isfile(os.path.join(COMPONENT_DIR, f"{platform}.yaml")), f"missing {platform}.yaml"


def test_every_yaml_file_parses():
    for path in glob.glob(os.path.join(COMPONENT_DIR, "*.yaml")):
        with open(path, encoding="utf-8") as handle:
            yaml.safe_load(handle)  # raises on invalid YAML


@pytest.mark.parametrize("platform", PLATFORMS)
def test_entities_have_id(platform):
    for entity in _load(platform):
        assert entity.get("id"), f"{platform} entity without id: {entity}"


def test_sensor_entities_declare_valid_source():
    # sensor.py requires an explicit, valid 'source' per entity.
    for entity in _load("sensor"):
        source = entity.get("source")
        assert source in VALID_SOURCES, f"sensor '{entity.get('id')}' has bad source: {source}"


def test_namespacelist_entities_specify_indexes():
    # A namespacelist source needs namespace_id + value_id to resolve a state.
    for platform in PLATFORMS:
        for entity in _load(platform):
            if entity.get("source") == "namespacelist":
                assert "namespace_id" in entity, f"{entity.get('id')} missing namespace_id"
                assert "value_id" in entity, f"{entity.get('id')} missing value_id"


def test_attribute_props_map_attribute_names_to_property_ids():
    # attribute_props is a flat "<attribute name>: <property id>" mapping that
    # entities.py reads with GetChargerProp; anything else cannot resolve.
    for platform in PLATFORMS:
        for entity in _load(platform):
            attribute_props = entity.get("attribute_props")
            if attribute_props is None:
                continue
            assert isinstance(attribute_props, dict), f"{entity.get('id')} attribute_props is not a mapping"
            for name, prop_id in attribute_props.items():
                assert isinstance(name, str) and name, f"{entity.get('id')} attribute_props has an empty name"
                assert isinstance(prop_id, str) and prop_id, f"{entity.get('id')} attribute_props.{name} is not an id"


def test_value_props_map_raw_codes_to_property_ids():
    # value_props swaps a raw code for the value of the property it points at, so
    # its keys must be the codes the charger reports (ints, as for 'enum') and its
    # values property ids GetChargerProp can resolve.
    for platform in PLATFORMS:
        for entity in _load(platform):
            value_props = entity.get("value_props")
            if value_props is None:
                continue
            assert isinstance(value_props, dict), f"{entity.get('id')} value_props is not a mapping"
            for code, prop_id in value_props.items():
                assert isinstance(code, int), f"{entity.get('id')} value_props key is not a raw code: {code!r}"
                assert isinstance(prop_id, str) and prop_id, f"{entity.get('id')} value_props.{code} is not an id"


def test_card_energy_sensors_declare_no_default_state():
    # The flat 'cNe' card sensors coexist with the legacy 'cards_N' namespacelist
    # ones, and rely on being skipped at init when the charger does not report
    # them. A default_state would break that: GetChargerProp returns the default
    # instead of None for an absent property, so the entity would be created and
    # sit at that default forever.
    flat = [e for e in _load("sensor") if re.fullmatch(r"c\de", str(e.get("id")))]
    assert len(flat) == 10, f"expected ten flat card-energy sensors, found {len(flat)}"
    for entity in flat:
        assert "default_state" not in entity, f"{entity.get('id')} must not set default_state"


# Charger keys that const.py::REDACT_ALLPROPS redacts but an entity exposes anyway, each with
# the reason it is acceptable. Everything else in REDACT_ALLPROPS must stay out of
# entity states, attributes and events: they all reach the recorder and every
# subscriber. Credentials never belong here.
EXPOSED_REDACTED_KEYS = {
    **{f"c{slot}n": "RFID card name: a user-chosen label, kept at the HACS reviewer's request" for slot in range(10)},
    "cards": "legacy RFID card list: only the card name and energy are exposed, never the cardId",
    "ccw": "WiFi Connection sensor: the SSID plus ip/netmask/gw/channel, but never the bssid",
}
CREDENTIALS = {"cak", "facwak", "ocppcc", "ocppck", "ocppsc", "wak"}

# Fields inside an exposed object value that must never become a state attribute.
FORBIDDEN_ATTRIBUTE_IDS = {
    "bssid": "the access point's MAC address, which can be looked up to a physical location",
    "cardId": "the RFID card identifier, which is what unlocks the charger",
}


def _module_literal(filename: str, name: str):
    """Read a module-level literal without importing the module (which needs Home Assistant)."""
    with open(os.path.join(COMPONENT_DIR, filename), encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == name:
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in {filename}")


def _exposed_charger_keys() -> dict[str, set[str]]:
    """Map every charger key an entity reads to the entities reading it."""
    exposed: dict[str, set[str]] = {}
    for platform in PLATFORMS:
        for entity in _load(platform):
            name = f"{platform}.{entity.get('uid') or entity.get('id')}"
            source = entity.get("source", "property")
            keys = list((entity.get("attribute_props") or {}).values())
            keys += list((entity.get("value_props") or {}).values())
            if entity.get("options_property"):
                keys.append(entity["options_property"])
            if source == "property":
                keys.append(entity.get("id"))
            elif source == "namespacelist":
                # 'cards_0' reads item 0 of the 'cards' property.
                keys.append(re.sub(r"_\d+$", "", str(entity.get("id"))))
            for key in keys:
                exposed.setdefault(str(key), set()).add(name)
    return exposed


def test_no_entity_exposes_a_redacted_key_without_a_reason():
    redacted = _module_literal("const.py", "REDACT_ALLPROPS")
    exposed = _exposed_charger_keys()
    unexplained = {k: sorted(v) for k, v in exposed.items() if k in redacted and k not in EXPOSED_REDACTED_KEYS}
    assert not unexplained, (
        f"entities expose keys that diagnostics redacts: {unexplained}. Leave them out, or add the key to "
        "EXPOSED_REDACTED_KEYS with the reason it is safe"
    )


def test_exposed_redacted_keys_are_still_redacted_and_used():
    # Keeps the exception list honest: an entry must still be redacted in
    # diagnostics, still be read by an entity, and never be a credential.
    redacted = _module_literal("const.py", "REDACT_ALLPROPS")
    exposed = _exposed_charger_keys()
    assert CREDENTIALS <= redacted, f"credentials not redacted in diagnostics: {sorted(CREDENTIALS - redacted)}"
    for key in EXPOSED_REDACTED_KEYS:
        assert key not in CREDENTIALS, f"{key} is a credential and can never be exposed"
        assert key in redacted, f"{key} is no longer redacted in diagnostics; drop it from EXPOSED_REDACTED_KEYS"
        assert key in exposed, f"no entity reads {key} any more; drop it from EXPOSED_REDACTED_KEYS"


def test_no_credential_is_exposed():
    exposed = _exposed_charger_keys()
    leaked = {k: sorted(exposed[k]) for k in CREDENTIALS if k in exposed}
    assert not leaked, f"credentials exposed by entities: {leaked}"


def test_no_event_fires_a_redacted_key():
    # Events are stored by the recorder and reach every subscriber.
    redacted = _module_literal("const.py", "REDACT_ALLPROPS")
    event_props = set(_module_literal("const.py", "EVENT_PROPS"))
    assert not event_props & redacted, f"EVENT_PROPS fires redacted keys: {sorted(event_props & redacted)}"


@pytest.mark.parametrize("field", sorted(FORBIDDEN_ATTRIBUTE_IDS))
def test_no_entity_exposes_a_forbidden_attribute(field):
    # Why each field is forbidden is recorded in FORBIDDEN_ATTRIBUTE_IDS.
    for platform in PLATFORMS:
        for entity in _load(platform):
            assert field not in (entity.get("attribute_ids") or []), (
                f"{platform}.{entity.get('uid') or entity.get('id')} exposes {field}: {FORBIDDEN_ATTRIBUTE_IDS[field]}"
            )


def test_unique_ids_are_unique_per_platform():
    # entities.py builds unique_id from uid|id; collisions would clobber entities.
    # Definitions sharing a uid are only legal when a gate (variant/connection/
    # firmware) makes them mutually exclusive at runtime — e.g. the 11kW vs 22kW
    # 'amp' number. Key uniqueness by (uid, gates) to allow those pairs.
    for platform in PLATFORMS:
        seen: set[tuple] = set()
        for entity in _load(platform):
            uid = entity.get("uid", entity.get("id"))
            key = (
                uid,
                entity.get("variant"),
                entity.get("connection"),
                entity.get("firmware"),
            )
            assert key not in seen, f"duplicate ungated uid '{uid}' in {platform}.yaml"
            seen.add(key)


def test_firmware_gate_uses_known_operator():
    valid_prefixes = (">=", "<=", "==", ">", "<")
    for platform in PLATFORMS:
        for entity in _load(platform):
            fw = entity.get("firmware")
            if fw is not None:
                assert str(fw).startswith(valid_prefixes), f"{entity.get('id')} bad firmware gate: {fw}"
