# MNEMOSYNE

**Selective KDE Configuration Persistence Engine**

[![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange)]()
[![Engine](https://img.shields.io/badge/engine-E--0.1.0--1-blue)]()
[![Platform](https://img.shields.io/badge/platform-Linux-informational)]()

MNEMOSYNE is a lightweight persistence engine designed to selectively preserve KDE configuration settings across Linux sessions.

Instead of saving entire configuration files, MNEMOSYNE stores individual configuration values and restores them when needed.

## Features

- **Selective persistence** – Save only the settings you actually need.
- **Capture** – Store individual KDE configuration values.
- **Apply** – Restore a specific saved setting.
- **Apply-all** – Restore all saved settings.
- **List** – Display stored settings.
- **Atomic manifest writes** – Protect the manifest during updates.
- **Path validation** – Restrict configuration access to the user's KDE configuration directory.

## Supported value types

| Type | Description |
|---|---|
| `string` | Text values |
| `int` | Integer values |
| `double` | Decimal values |
| `bool` | Boolean values |

## Requirements

- Linux
- KDE Plasma
- Python 3
- KDE configuration utilities (`kreadconfig6` and `kwriteconfig6`)

## Usage

Run the engine using Python:

```bash
python3 "MNEMOSYNE - Persistence Engine.py" --help
```

Capture a setting:

```bash
python3 "MNEMOSYNE - Persistence Engine.py" capture kwinrc Xwayland Scale double
```

Apply a saved setting:

```bash
python3 "MNEMOSYNE - Persistence Engine.py" apply kwinrc Xwayland Scale
```

Restore all saved settings:

```bash
python3 "MNEMOSYNE - Persistence Engine.py" apply-all
```

Display saved settings:

```bash
python3 "MNEMOSYNE - Persistence Engine.py" list
```

## Project structure

```text
MNEMOSYNE/
├── MNEMOSYNE - Persistence Engine.py
├── manifest.json
├── README.md
├── LICENSE
└── documentation/
    └── RELEASE_NOTES.md
```

## Versioning

Current release: **MNEMOSYNE v0.1.0 Alpha**

Engine identifier: `E-0.1.0-1`

Manifest schema version: `1`

## Development status

MNEMOSYNE is currently in **Alpha**.

Core functionality has been implemented and tested, including capturing settings, restoring individual settings and restoring all saved settings.

Further testing and development are planned.

## License

See the `LICENSE` file for licensing information.
