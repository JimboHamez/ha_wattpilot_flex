[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
![GitHub Release](https://img.shields.io/github/v/release/JimboHamez/ha_wattpilot_flex?style=for-the-badge)
[![Installs](https://img.shields.io/badge/dynamic/json?color=41BDF5&style=for-the-badge&logo=home-assistant&label=installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.wattpilot_flex.total)](https://analytics.home-assistant.io/custom_integrations.json)
[![Quality Scale](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FJimboHamez%2Fha_wattpilot_flex%2Fmain%2Fcustom_components%2Fwattpilot_flex%2Fmanifest.json&query=%24.quality_scale&label=Quality%20Scale&style=for-the-badge&color=E5E4E2)](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
![GitHub License](https://img.shields.io/github/license/JimboHamez/ha_wattpilot_flex?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/JimboHamez/ha_wattpilot_flex?style=for-the-badge)
![Maintenance](https://img.shields.io/maintenance/yes/2026?style=for-the-badge)

[![Tests](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/test.yml/badge.svg)](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/test.yml)
[![Validate](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/validate.yaml/badge.svg)](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/validate.yaml) [![hassfest](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/hassfest.yaml)
[![Security](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/security.yml/badge.svg)](https://github.com/JimboHamez/ha_wattpilot_flex/actions/workflows/security.yml)

> **Note:** This repository began as a fork of
> [mk-maddin/wattpilot-HA](https://github.com/mk-maddin/wattpilot-HA) by Martin Kraemer
> ([@mk-maddin](https://github.com/mk-maddin)), and the original design is his — full credit
> belongs upstream, and it is redistributed here under its original [Apache-2.0](LICENSE) license.
>
> **The two have since diverged substantially.** As of 0.5.0 this fork replaced the vendored,
> synchronous `wattpilot` library with the maintained async
> [`wattpilot-api`](https://pypi.org/project/wattpilot-api/), rewrote the entities around it,
> added translated names and states, mDNS discovery, reauthentication and reconfiguration flows,
> and now meets every rule of the Home Assistant Integration Quality Scale (self-declared
> **platinum**). Behaviour, entity names and entity units differ from upstream in ways upstream
> cannot support.
>
> **Please report issues with *this* integration
> [here](https://github.com/JimboHamez/ha_wattpilot_flex/issues), not upstream.** Bug reports about
> this fork's code are not upstream's to answer. Go to
> [mk-maddin/wattpilot-HA](https://github.com/mk-maddin/wattpilot-HA) if you are running
> the original integration.

> **Upgrading from 0.12.x or earlier?** The integration's domain changed from `wattpilot` to
> `wattpilot_flex` in 1.0.0, and your chargers have to be added again once. Follow
> [Moving from the `wattpilot` domain](#moving-from-the-wattpilot-domain) **before** you update.

# What This Is:

This is a custom component to allow control of [Fronius Wattpilot](https://www.fronius.com/en/solar-energy/installers-partners/technical-data/all-products/solutions/fronius-wattpilot/fronius-wattpilot/wattpilot-home-11-j) wallbox/electro vehicle charging devices in [Homeassistant](https://home-assistant.io) using the unofficial, reverse-engineered [`wattpilot-api`](https://pypi.org/project/wattpilot-api/) Python library, which talks to the charger over its WebSocket API (locally on the LAN, or via the go-e cloud).

WARNING:
There is no official Fronius API. This integration is built entirely on a community, reverse-engineered library and may break at any time (for example after a charger firmware update).

## Disclaimer:

As written this is an unofficial implementation.
Currently there does not seem to be an official API available by fronius, so this is all based on the work of volunteers and hobby programmers.
It might stop working at any point in time.

You are using this module (and it's prerequisites/dependencies) at your own risk.
Not me neither any of contributors to this or any prerequired/dependency project are responsible for damage in any kind caused by this project or any of its prerequsites/dependencies.

# What It Does:

Allows for control of [Fronius Wattpilot](https://www.fronius.com/en/solar-energy/installers-partners/products-solutions/residential-energy-solutions/e-mobility-and-photovoltaic-residential/wattpilot-ev-charging-solution-for-homes) wallbox/electro vehicle charging devices via home assistant with the following features:

* works with wattpilot, wattpilot V2 & wattpilot flex
* connect charger via local LAN or via Cloud
* automatic discovery of chargers on your local network (mDNS/zeroconf)
* re-authentication prompt if the charger password changes
* charging mode change
* start / stop charging
* configuration for different charging behaviours
* sensors for charging box status
* manual disconnect/reconnect chargers (Helpful for Wattpilot GO version)
* next trip timing configuration via service call (& event when next trip timing value is changed) -> you can create an [input_datetime (example)](packages/wattpilot/wattpilot_input_datetime.yaml) entity & corresponding [automation (example)](packages/wattpilot/wattpilot_automation.yaml) which ensures the input_datetime is in sync with the setting wihtin your wattpilot charger
* log value changes for properties of the wallbox as warnings (enable/disable via service call)
* can enable/disable e-go cloud charging API (enable/disable via service call) -> this is at your own responsibility - is not clear if fronius/you "pay" in some way for the e-go cloud API and thus are legally allowed to use -> as it is not required at the moment for the functionality of this component, I do not recommend to enable

## Use cases

What people actually use this for:

* **Charge the car on solar surplus only.** Turn on *PV Surplus* and set *Start Charging at*
  to the surplus power that should trigger charging; the charger then follows your PV
  production instead of the grid. Home Assistant gives you the missing half — pause it when the
  house battery drops below a threshold, or force a full-power session when you need the car
  sooner.
* **Be ready for a trip without leaving the car on the grid all night.** Set the departure time
  and the energy you need, and the charger works backwards from it. The `set_next_trip` action
  writes that departure time, so it can follow a calendar or an `input_datetime` helper rather
  than being typed into the app (see the example below).
* **See and set the app's charging times from Home Assistant.** The three *Charging Schedule*
  sensors (weekdays / Saturday / Sunday) show whether charging is limited to the app's time
  windows, whether PV surplus may charge outside them, and the windows themselves; the
  `set_charging_schedule` action changes any of that — e.g. widen the window on a public
  holiday, or turn the limit off when a cheap-rate event is announced.
* **Charge when electricity is cheap.** Point the *Charging Mode* select at Eco and let the
  charger use the aWattar/Lumina price feed, or drive *Max Charging Current* yourself from any
  price sensor you already have in Home Assistant (or *Charging Current Preset* if you want the
  app's slider to follow — see [Known limitations](#known-limitations)).
* **See what the wallbox is doing, and record it.** *Charging Power*, *Totally Charged* and
  *Connection Charged* are proper energy/power entities, so they slot straight into the Energy
  dashboard and long-term statistics; *ChargingReason* tells you why charging is (not) running
  right now.
* **Keep a Wattpilot GO usable.** The `disconnect_charger` / `reconnect_charger` actions free
  the charger's single WebSocket session so the phone app can take over, then take it back.

## Example automations

The [`packages/wattpilot/`](packages/wattpilot) folder holds ready-to-use configuration:
[`wattpilot_input_datetime.yaml`](packages/wattpilot/wattpilot_input_datetime.yaml) and
[`wattpilot_automation.yaml`](packages/wattpilot/wattpilot_automation.yaml) keep an
`input_datetime` helper and the charger's next-trip time in sync in both directions, and
[`wattpilot_logger.yaml`](packages/wattpilot/wattpilot_logger.yaml) turns on debug logging.
Copy them into your `packages/` directory and replace the `device_id` with your charger's.

Two smaller examples to start from — both use the entity names this integration ships, so
adjust the entity ids to match your charger's device name:

```yaml
# Pause surplus charging while the house battery is low, resume when it recovers.
automation:
  - alias: Wattpilot - protect the house battery
    triggers:
      - trigger: numeric_state
        entity_id: sensor.house_battery_level
        below: 30
        id: low
      - trigger: numeric_state
        entity_id: sensor.house_battery_level
        above: 50
        id: recovered
    actions:
      - choose:
          - conditions: "{{ trigger.id == 'low' }}"
            sequence:
              - action: switch.turn_off
                target:
                  entity_id: switch.wattpilot_pv_surplus
          - conditions: "{{ trigger.id == 'recovered' }}"
            sequence:
              - action: switch.turn_on
                target:
                  entity_id: switch.wattpilot_pv_surplus
```

```yaml
# Set the next-trip departure time from a calendar event.
automation:
  - alias: Wattpilot - next trip from calendar
    triggers:
      - trigger: calendar
        entity_id: calendar.commute
        event: start
        offset: "-12:00:00"
    actions:
      - action: wattpilot_flex.set_next_trip
        data:
          device_id: !secret wattpilot_device_id
          # trigger_time is a time of day (HH:MM:SS), not a full timestamp.
          trigger_time: "{{ trigger.calendar_event.start | as_datetime | as_local | strftime('%H:%M:%S') }}"
```

```yaml
# Widen the weekday charging window when the retailer announces a free-power event,
# and put the normal schedule back afterwards. The action reads the current schedule
# and rewrites it with only the fields given here changed.
automation:
  - alias: Wattpilot - free power event
    triggers:
      - trigger: state
        entity_id: binary_sensor.free_power_event
        to: "on"
        id: start
      - trigger: state
        entity_id: binary_sensor.free_power_event
        to: "off"
        id: end
    actions:
      - action: wattpilot_flex.set_charging_schedule
        data:
          device_id: !secret wattpilot_device_id
          day_type: weekdays
          ranges: >
            {{ [{'begin': '00:00', 'end': '23:59:59'}] if trigger.id == 'start'
               else [{'begin': '00:00', 'end': '06:00'}, {'begin': '08:00', 'end': '15:00'}] }}
```

## Open Topics:

* create a light integration for LED color control etc.
* expose the app-only `cco` / `dwo` properties — see
  [doc/charging-schedule-and-app-properties.md](doc/charging-schedule-and-app-properties.md)
  (the charging schedule itself is now exposed — see [Actions](#actions))
* dynamic pricing: expose `awpl` / `awcp`, and feed the charger an Amber Electric price
  list or drive `frc` from Amber in HA — see
  [doc/dynamic-pricing-and-amber.md](doc/dynamic-pricing-and-amber.md)

## Reporting issues:

Issues for this fork are tracked at
[JimboHamez/ha_wattpilot_flex/issues](https://github.com/JimboHamez/ha_wattpilot_flex/issues) — please
report them there rather than upstream, since this code has diverged from the original.

When reporting, include the integration version, your charger model/variant and firmware, the
[debug log](#troubleshooting) for the affected entity, and (if possible) the redacted
**diagnostics** download from the device page.

# Screenshots

### Example Device (additional sensors + buttons can be enabled)

![screenshot of Wattpilot Device](doc/device_view1.jpg)

![screenshot of Wattpilot Device](doc/device_view2.jpg)

![screenshot of Wattpilot Device](doc/device_view3.jpg)

### Next Trip via timing via Service Call

![screenshot of Next Trip service](doc/service_view1.jpg)

# Installation and Configuration

## Installation

Install it either through HACS, which is recommended and keeps it up to date, or manually (see
[Install manually](#install-manually)).

### Install with HACS

With [HACS](https://hacs.xyz/) installed:

1. In Home Assistant, open **HACS** and search for **Fronius Wattpilot Flex**, or open it directly:
   [![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JimboHamez&repository=ha_wattpilot_flex&category=integration)
2. Select **Download**, then restart Home Assistant.
3. Add the charger as described under Configuration below.

HACS keeps track of updates from then on.

If the search finds nothing, your HACS has not picked up the integration's default-catalog entry
yet: add `https://github.com/JimboHamez/ha_wattpilot_flex` as a
[custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (type **Integration**) and search again.

### Install manually
Download the repository and save the `custom_components/wattpilot_flex` folder into your home assistant custom_components directory.

Once the files are downloaded, you’ll need to **restart HomeAssistant** and wait some minutes (probably clear your browser cache),
for the integration to appear within the integration store.

## Moving from the `wattpilot` domain

Up to 0.12.x this integration used the domain `wattpilot`, the same as
[mk-maddin/wattpilot-HA](https://github.com/mk-maddin/wattpilot-HA), the project it started
from. Two integrations cannot share one domain, because both install into
`custom_components/wattpilot` and whichever is installed second overwrites the other. The
original project had the domain first, so from **1.0.0** this one is `wattpilot_flex`, and it
shows in Home Assistant as **Wattpilot Flex**.

Home Assistant treats a new domain as a new integration, so existing charger entries do not
carry over and each charger has to be added again once.

**What carries over:** entity IDs, and with them the state history and long-term statistics
(energy dashboard included), as long as the re-added entities get the same IDs. They are built
from the charger's device name, so they match when you give the charger the same name as before
and have not renamed an entity yourself.

**What does not carry over:** entity and device renames, areas, labels, which entities you
enabled or disabled, and the device ID. Action names, the event name and the logger name change
too (see step 7).

1. **Before updating**, write down what you have customised: renamed entities, areas, the
   entities you enabled (many are disabled by default), and the automations, scripts and
   dashboards that use the actions, the event or the charger's device.
2. Go to **Settings → Devices & services → Fronius Wattpilot** (the old integration's name) and
   **Delete** each charger entry
   (⋮ menu on the entry). Do this first. An entry left behind keeps its entity IDs reserved, and
   the re-added entities then get a `_2` suffix and start a fresh history. If you have already
   updated, the old entries are still listed as failing to load, and you can delete them the
   same way.
3. Update the integration in HACS (or, for a manual install, copy in the new
   `custom_components/wattpilot_flex` folder). Then delete the old `custom_components/wattpilot`
   folder if it is still there, unless you installed mk-maddin's integration into it on purpose.
4. Restart Home Assistant.
5. Add the charger again as **Wattpilot Flex** (see [Configuration](#configuration)), or accept
   it when it is discovered, with the same connection details and the **same name** as before.
6. Check that the entity IDs match the old ones. Rename any that do not back to the old ID so its
   history continues. Then re-apply your areas, names and enabled entities.
7. Update automations, scripts and configuration:

   | Before | From 1.0.0 |
   |--------|-------------|
   | `wattpilot.set_next_trip` and the other actions | `wattpilot_flex.set_next_trip`, … |
   | event `wattpilot_property_message` | event `wattpilot_flex_property_message` |
   | logger `custom_components.wattpilot` | logger `custom_components.wattpilot_flex` |
   | the charger's old `device_id` (actions, device triggers) | pick the re-added device again |

   The [example packages](packages/wattpilot) already use the new names.

## Configuration

### Using MyHA:

[MyHA - Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=wattpilot_flex)

### Manually:

1. Browse to your Home Assistant instance.
2. In the sidebar click on Configuration.
3. From the configuration menu select: Integrations.
4. In the bottom right, click on the Add Integration button.
5. From the list, search and select "Wattpilot Flex".
6. Follow the instruction on screen to complete the set up.
   (If connecting local/LAN you will require the local IP - for cloud connection your wattpilot serial is required)

![screenshot of Config Flow](doc/config_flow1.jpg)

Chargers on your local network are usually **discovered automatically** — when one
is found, Home Assistant shows it under **Settings → Devices & services** and only
asks for the charger password.

## Configuration parameters

The setup wizard first asks how to connect, then for the matching details:

| Parameter | Connection | Description |
|-----------|-----------|-------------|
| Connection type | both | `Local (LAN)` connects directly to the charger's IP; `go-e Cloud` connects through the go-e cloud using the serial number. |
| Name | both | Display name for the charger in Home Assistant. |
| IP address | local | Local IP address of the charger on your network. |
| Serial number | cloud | Serial number of the charger (used to reach it via the go-e cloud). |
| Password | both | The charger password configured in the Wattpilot app. |
| Timeout | both | Seconds to wait for the connection to be established and initialised (default 15). |

You can change these later without removing the charger, via **Reconfigure** in the entry's
⋮ menu. It tests the new details before saving them, reloads the entry, and checks that the
details still point at *this* charger — so correcting an IP address after the charger moved
cannot silently rebind the entry to a different one. The connection type (local or cloud)
cannot be switched there; add the charger again for that.

> **Changed in 0.8.0:** the separate **Configure** dialog has been removed — everything it
> did now lives in **Reconfigure**, which validates more and is where Home Assistant expects
> connection settings to be. Your existing settings are unaffected.

If the charger password changes, Home Assistant raises a **reauthentication** prompt asking
you to enter the new one.

## Actions

Everything you can set day to day is an entity — these actions cover the rest. All of them
take a **Charger** (`device_id`) and are available under **Developer Tools → Actions** and in
automations.

| Action | Parameters | What it does |
|--------|-----------|--------------|
| `wattpilot_flex.set_next_trip` | `trigger_time` (time of day, e.g. `06:30:00`) | Sets the departure time used by the Next Trip charging mode, as a time of day on the charger's own clock. The charger applies its time zone and daylight saving itself, whatever time zone Home Assistant runs in. Also fires a `wattpilot_flex_property_message` event whenever the charger's own next-trip time changes, so a helper can be kept in sync. |
| `wattpilot_flex.set_charging_schedule` | `day_type` (`weekdays`, `saturday` or `sunday`), then any of `limit_charging_times` (boolean), `pv_surplus_outside_times` (boolean), `ranges` (list of `{begin: "HH:MM", end: "HH:MM"}`) | Writes one day type of the app's charging times. The charger only takes the whole schedule object, so the action reads the current one and rewrites it with the fields you supply changed — leave a field out to keep it. Windows are checked before anything is written: each must end after it begins on the same day (a window over midnight is split into an evening and a morning one, as the app does — each day type has its own schedule) and they must not overlap. The matching *Charging Schedule* sensor shows the result: state is the mode, the windows and flags are attributes. |
| `wattpilot_flex.set_goe_cloud` | `cloud_api` (boolean) | Enables or disables go-e cloud API access and caches the returned key/URL. Enabling is at your own responsibility — see the note under [What It Does](#what-it-does). |
| `wattpilot_flex.set_debug_properties` | `debug_properties` (`true`, `false`, or a list of property codes) | Logs charger property changes as warnings. `true` logs everything (noisy), a list logs only those codes — e.g. `[wda, cci, err]`. |
| `wattpilot_flex.disconnect_charger` | – | Closes the charger's WebSocket session; its entities go unavailable. Useful on a Wattpilot GO, which allows only one connection at a time, when you want the phone app to take over. |
| `wattpilot_flex.reconnect_charger` | – | Reopens the session after `disconnect_charger`, or forces a reconnect. |

Failures surface as errors on the calling script rather than being silently logged, so an
automation stops when a charger cannot carry out what it was asked. The same holds for the
entities' own actions: turning a switch on or off, pressing a button, picking a select option,
setting a number or installing a firmware update all raise an error when the charger does not
take the change. To let an automation carry on past such a step, add `continue_on_error: true`
to it.

## Supported devices

Fronius Wattpilot **Home / Home 2 / V2 / Flex**, in both the **11 kW** and **22 kW**
variants (the correct entities are enabled automatically for your variant). The
integration is developed against a physical **Wattpilot Flex (22 kW, firmware 43.4)**;
other models rely on the community library and may expose a slightly different set of
properties.

## How data updates work

The integration is **local push** (`iot_class: local_push`): it keeps a WebSocket
open to the charger and updates entities immediately when the charger reports a
property change. A small poll fallback seeds the initial value of each entity and
covers the few attributes the charger does not push. Because it is push-based, there
is no polling interval to configure.

## Under the hood: `wattpilot-api`

Since **0.5.0** this integration talks to the charger through the maintained, **async**
[`wattpilot-api`](https://pypi.org/project/wattpilot-api/) library (`wattpilot-api>=1.4.0`,
installed automatically from `manifest.json`). It replaced the original project's *vendored*
copy of the synchronous [`wattpilot`](https://github.com/joscha82/wattpilot) module, which was
shipped inside the component and driven from a background thread.

What that means in practice:

- The WebSocket connection is native `asyncio`, so nothing blocks Home Assistant's event loop
  and property updates reach entities directly instead of being marshalled across threads.
- The library is a normal dependency, so it is installed and updated by Home Assistant like any
  other requirement — no vendored code to keep in sync.
- It is still a **community, reverse-engineered** library: there is no official Fronius API, and
  a charger firmware update can break it.

This is the main reason this fork's behaviour differs from upstream, and why issues belong
[here](https://github.com/JimboHamez/ha_wattpilot_flex/issues).

## Entity units

The charger reports raw values in the units its firmware happens to use — milliseconds, watts,
watt-hours. Those are awkward to read and to set, so the integration presents several entities
in human-scale units instead. **The charger still receives its native units**; the conversion is
in the integration.

| Entity | Charger sends | Shown in Home Assistant |
|---|---|---|
| Min Charging Time (`fmt`) | milliseconds | **minutes** (1–60) |
| Next Trip Charging (`fte`) | Wh | **kWh** (5–120, slider) |
| Start Charging at (`fst`) | W | **kW** (1.4–22) |
| 3-Phase power level (`spl3`) | W | **kW** (0–22) |
| Charging Power (`nrg`) | W | **kW** |
| Totally Charged (`eto`), Connection Charged (`wh`), ID Chip counters | Wh | **kWh** |

Two different mechanisms do this, and the difference matters if you look closely:

- The **numbers** (`fmt`, `fte`, `fst`, `spl3`) are rescaled by the integration, so their
  recorded value itself changes scale.
- The **sensors** (`nrg`, `eto`, `wh`, ID chips) keep their native unit and use Home Assistant's
  own unit conversion, so long-term statistics stay continuous and you can override the displayed
  unit per entity from the entity settings.

> **Upgrading from 0.5.1 or earlier:** the four numbers above change scale, so their history shows
> a step at the upgrade, and any automation or dashboard that referenced them in raw ms/W/Wh must
> be updated (e.g. a `Start Charging at` of `4000` now means 4000 kW, not 4000 W — set `4.0`).
> Per-phase powers exposed as *attributes* of Charging Power (`L1_Power`, `TotalPower`, …) are
> **not** converted and remain in watts.

## Charging schedule

The app's *charging times* screen — one schedule each for **weekdays**, **Saturday** and
**Sunday**, with a *Limit charging times* toggle, a *Charge with PV surplus* toggle and a list
of time windows — is stored on the charger as three properties (`sch_week`, `sch_satur`,
`sch_sund`). The integration shows and sets them:

- **Three *Charging Schedule* sensors.** The state is the schedule's mode: `Off`, `Charging
  times` (charge only inside the windows), `PV surplus outside times`, or `Charging times + PV
  surplus outside` (both toggles on — the usual setting). The windows and flags are attributes:

  | Attribute | Example | Meaning |
  |---|---|---|
  | `ranges` | `[{begin: "00:00", end: "06:00"}, {begin: "08:00", end: "15:00"}]` | The charging windows, as the app shows them |
  | `limit_charging_times` | `true` | *Limit charging times* toggle |
  | `pv_surplus_outside_times` | `true` | *Charge with PV surplus* toggle |
  | `control` | `3` | The charger's raw value (bit 0 = limit, bit 1 = PV surplus) |

- **The `set_charging_schedule` action** writes one day type back (see [Actions](#actions)).
  Give it `day_type` and any of `limit_charging_times`, `pv_surplus_outside_times` and
  `ranges`; whatever you leave out keeps its current value.

Rules the action enforces **before** anything is sent to the charger, each reported as an
error on the calling automation:

- Every window must **end after it begins on the same day**. Each day type has its own
  schedule, so a window like `22:00 → 06:00` cannot run over midnight into the next one — split
  it into `22:00 → 23:59:59` and `00:00 → 06:00`, which is what the app does too.
- Windows must **not overlap**. They may touch (`06:00 → 08:00` then `08:00 → 10:00`), and the
  order you list them in does not matter.
- Times are `HH:MM` or `HH:MM:SS`.

Whether the charger honours a schedule is visible in *ChargingReason*: `NotChargingBecauseScheduler`
means a window is blocking charging right now. Note the app writes only the day type being
edited, so changing weekdays in the app never touches Saturday or Sunday — the same is true of
the action.

> The charger's `control` field is a **bitmask** on Fronius firmware, not the
> `Disabled / Inside / Outside` enum the community API definition documents (which is what a
> go-e charger uses). The integration decodes the two bits and passes anything else through as
> the raw `control` attribute rather than rejecting it. Verified on a Flex, firmware 43.4 — see
> [doc/charging-schedule-and-app-properties.md](doc/charging-schedule-and-app-properties.md).

## Local Time (charger clock vs HA clock)

The **Local Time** sensor (disabled by default, diagnostic) reports the charger's own clock as a
proper timestamp. Home Assistant renders timestamp sensors as *relative* time, so it will read
something like *"In 4 seconds"* or *"2 minutes ago"* rather than a wall-clock time.

That is not a bug — and it is the useful part: **the relative reading is the drift between your
charger's clock and Home Assistant's clock.** A few seconds is normal. A large or growing offset
is worth investigating, because the charger's own clock is what drives time-dependent behaviour
such as next-trip charging and daylight-saving handling (`tds`) — if the charger thinks it is an
hour off, your next trip will charge an hour off.

To see the absolute time instead, click the entity (the more-info dialog shows the full date and
time), or set the row format in a dashboard:

```yaml
type: entities
entities:
  - entity: sensor.<your_charger>_local_time
    format: datetime   # or date / time / relative / total
```

In templates and automations the state is already a `datetime`, so `as_timestamp()` and friends
work on it directly.

## Known limitations

- There is **no official Fronius API** — everything is built on the reverse-engineered
  [`wattpilot-api`](https://pypi.org/project/wattpilot-api/) library and may break
  after a charger firmware update.
- Requires **Python 3.12+** (a modern Home Assistant release satisfies this).
- On Home Assistant releases **before 2026.3** the integration shows no icon. Those releases
  take icons only from the brands repository, which no longer accepts new custom integrations;
  2026.3 and later use the images bundled with the integration.
- Local mode needs the charger reachable on your LAN; cloud mode needs the go-e cloud
  reachable and the charger's serial number.
- Some entities are **disabled by default** (diagnostics, rarely-used settings) — enable
  them from the device page if you need them.
- The go-e cloud charging API toggle is provided for convenience but is your own
  responsibility to use; it is not required for this integration to work.
- The Fronius app's charging-speed **slider only has stops at its presets** (10, 16, 20, 24
  and 32 A on a 22 kW charger — the charger's `clp` list). The *Max Charging Current* number
  entity sets any 1 A step, and the charger accepts it — the app then shows the right kW figure
  but the slider does not move. If you want what you set in Home Assistant to land on a slider
  stop, use the *Charging Current Preset* select instead: its options are the charger's own
  presets, it writes the same setting, and it shows no selection while the current is between
  two presets.

## Troubleshooting

- **Charger shows as unavailable / fails to set up:** confirm the IP (local) or serial
  (cloud) and password, and that the charger is powered on and reachable. Setup retries
  automatically when the charger comes back.
- **"Invalid authentication" / reauth prompt:** the charger password changed — enter the
  new password when Home Assistant asks, or via **Reconfigure**.
- **Eco / PV-surplus charging keeps stopping, and `ChargingReason` reads
  `NotChargingBecauseFallbackAwattar`:** the charger is refusing to charge because the market
  price for the current hour is above **Max Price** (`awp`, in EUR cent). Observed on firmware
  43.4 **with the flexible tariff switch (`ful`) off**, alternating with
  `ChargingBecausePvSurplus` while solar was exporting — so the price rule is still consulted on
  the fallback path. It bites hardest outside the countries the feature covers: **Awattar Country**
  (`awc`) has 51 options with no "none" and no Australia, so the price feed cannot be turned off,
  and a low `awp` (3 cent, for instance) then blocks charging whenever the fetched price is higher.
  Raise the **Max Price** number entity to a value the price can never exceed (its maximum is
  999999) so the rule stops gating charging. Enable the `ChargingReason` sensor to see the
  charger's own reason at any moment.
- **Enable debug logging** to trace behaviour, then reproduce the issue:
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.wattpilot_flex: debug
  ```
- **Watch specific charger properties** as log warnings using the `wattpilot_flex.set_debug_properties`
  service, and download a redacted **diagnostics** file from the device page to share when
  reporting an issue.
- Services (`disconnect_charger`, `reconnect_charger`, `set_goe_cloud`, `set_debug_properties`,
  `set_next_trip`) are available under **Developer Tools → Actions**.

## Removing the integration

Go to **Settings → Devices & services**, open the Wattpilot Flex integration, and
use the menu on the charger entry to **Delete**. No files remain in your configuration;
if you installed manually, also remove the `custom_components/wattpilot_flex` folder.

# Credits:

Big thank you to the maintainers of [`wattpilot-api`](https://pypi.org/project/wattpilot-api/),
the async library this integration has talked to the charger through since 0.5.0 — without it
none of this would work.

Thanks also to [@mk-maddin](https://github.com/mk-maddin), whose
[wattpilot-HA](https://github.com/mk-maddin/wattpilot-HA) integration this is forked from and
whose data-driven entity design it still uses, and to
[@joscha82](https://github.com/joscha82), whose original reverse-engineering work in the
synchronous [`wattpilot`](https://github.com/joscha82/wattpilot) module got this whole thing
off the ground — it powered this integration up to 0.4.x and is still the reference for the
charger's WebSocket protocol.

# License

[Apache-2.0](LICENSE). By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.
